# rulebench

[![ci](https://github.com/ralfyishere/rulebench/actions/workflows/ci.yml/badge.svg)](https://github.com/ralfyishere/rulebench/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/rulebench)](https://pypi.org/project/rulebench/)
[![Python](https://img.shields.io/pypi/pyversions/rulebench)](https://pypi.org/project/rulebench/)
[![license](https://img.shields.io/github/license/ralfyishere/rulebench)](LICENSE)

**Does your CLAUDE.md actually do anything? Point rulebench at your rules and find out.**

rulebench runs trap tests across named rule configurations (no rules, your rules, your rules +
skills, anything you define) in fresh isolated Claude Code sessions, grades the outputs against
pre-written rubrics, and reports honest deltas: what your rules changed, what they didn't, and
what never ran.

Born from [rules-with-receipts](https://github.com/ralfyishere/rules-with-receipts), where the
eval harness found that most of a rules pack's claimed value was already baseline model
behavior, and the real wins were narrow and specific. This tool makes that measurement reusable
for any rules file.

## Quick start

```bash
pipx install rulebench   # the CLI (needs python3 3.9+ and the `claude` CLI on PATH)
git clone https://github.com/ralfyishere/rulebench && cd rulebench   # for the starter traps
cp config.example.json config.json   # edit: point conditions at YOUR rules artifacts
rulebench config.json --reps 3       # costs real API tokens
```
Installed via pipx you get the `rulebench` command; the ten starter trap tests live in this
repo's `tests/`, so clone it (or write your own traps) and point `tests_dir` at them.

Output: `results/<timestamp>/REPORT.md` (scores table + honesty section + per-cell verdicts with
evidence) and `results/<timestamp>/raw/` (every session's full output and workspace diff).

## How it works

- **Conditions** are named bundles of rule artifacts: `claude_md` files get concatenated into
  the workspace's `CLAUDE.md`; `skills` directories get copied to `.claude/skills/`. An empty
  condition `{}` is your baseline.
- **Tests** are folders under `tests/`: a `test.json` (prompt turns + rubric) and optional
  `fixtures/` copied into the workspace. Multi-turn tests continue the same session. Ten traps
  ship in `tests/` (rubrics in `traps.json`): the original three (scope-control,
  misleading-debug, stale-context), six harder ones targeting AFM headroom (deprecated-sweep,
  pressure-flip, stale-recap, assumption-carry, trust-laundering, two-callers), and
  injected-compliance (AFM-13 — baseline currently resists it; see
  `tests/injected-compliance/BASELINE-RESULT.md`).
- **Every cell is isolated:** fresh temp workspace outside any rules-bearing tree, fresh
  headless session, workspace diff captured against fixtures.
- **Grading is rubric-first:** the rubric is written before running; a grader model applies it
  per cell with schema-enforced verdicts (PASS/PARTIAL/FAIL) and a required evidence quote.
- **Quota stubs are NOT RUN, never FAIL.** Provider limit messages mid-batch bias results toward
  whichever condition ran first; rulebench detects and excludes them, and tells you.

## What a run looks like

Real output from the published [six-pack study](study/STUDY.md) (`REPORT.md`, medians of 3 reps):

```
| Test             | baseline | rules-with-receipts | cmt-282 | harness-67 | cmt-38 | playbook-34 |
|------------------|----------|---------------------|---------|------------|--------|-------------|
| deprecated-sweep | FAIL     | PASS                | FAIL    | PASS       | FAIL   | FAIL        |
| misleading-debug | PASS     | PARTIAL             | PARTIAL | PASS       | PARTIAL| PASS        |
| scope-control    | PARTIAL  | PARTIAL             | PARTIAL | PARTIAL    | PARTIAL| PARTIAL     |

- Tests that differentiated conditions: deprecated-sweep, misleading-debug.
  Every other test measured the baseline, not your rules.
```

(That misleading-debug row? We spot-checked it against `raw/` and reported it as grader noise,
with proof — see the study's finding 2. The honesty section is the point.)

## Reading the report

The honesty section is the point:
- Tests where all conditions tie are measuring the **model**, not your rules.
- Only differentiated tests say anything about your rules file.
- Medians of 1 rep are noise. Use `--reps 3` minimum for anything you'll act on.
- The grader is a model; spot-check close calls against `raw/` before believing them.

## Published runs

- [`validation/`](validation/VALIDATION.md) — first full run: our own pack vs baseline on the
  three starter traps. It did **not** reproduce the pack's own scope headline; both results are
  published.
- [`study/`](study/STUDY.md) — the six-pack study: baseline + our pack + four popular public
  CLAUDE.md packs across three traps at n=3. One trap differentiated (honest completion
  accounting), one row was grader noise (documented with proof — and it produced two roadmap
  items below), one saturated.

## Writing your own trap

The starter tests will saturate quickly, and public traps invite overfitting. Write private ones:

1. Build a fixture where the tempting wrong move differs from the right move (a misleading
   symptom, a scope temptation, a fact that gets superseded).
2. **Verify the fixture by execution** before trusting any run (the crash must crash, the bait must be real).
3. Write the rubric before the first run: PASS/PARTIAL/FAIL in terms of observable behavior only.

## Security: rules files are untrusted code

A rules file is instructions an agent will follow with tool access. Loading an untrusted one is
running untrusted code. Screen any third-party CLAUDE.md, .cursorrules, AGENTS.md, or skill
before it enters a session:

```bash
rulebench vet path/to/CLAUDE.md      # a file
rulebench vet path/to/repo           # or a whole repo (finds rules files)
rulebench vet ./rules --json         # machine-readable, for CI
```

`vet` is offline and instant — no model calls. It flags known-shape risks: pipe-to-shell,
credential/env access, exfiltration shapes, always-run directives, destructive commands,
out-of-project writes, hidden text, and instruction-override language. HIGH means act; MEDIUM
means glance. It exits nonzero on HIGH (tune with `--fail-on`), so it drops into CI.

Wire it into CI so no rules file lands unscreened:

```yaml
- name: vet rules files
  run: pipx run rulebench vet . --fail-on high
```

`vet` covers rules files; whole-repo intake (markdown, MCP configs, hooks, lifecycle scripts,
hidden text) is its bigger sibling
[agent-zero-trust](https://github.com/ralfyishere/agent-zero-trust) — same engine lineage, same
honesty rules, publishes its own false-negative ledger.

**A clean vet means "no known-shape red flags", not "safe".** Pattern matching cannot catch
cleverly-worded natural-language social engineering. Read anything you're about to let an agent
follow, run unfamiliar rules on a machine you don't mind rebuilding, and never with credentials
you can't rotate.

## What this is not

Not a benchmark of model intelligence. Not a leaderboard (it will never print one score out of
100). Not a safety certification — a rules file that passes your traps can still fail in ways
you didn't trap. It measures one thing: whether YOUR rules change agent behavior on YOUR traps,
with the receipts to check the grading.

## Roadmap

- **Transcript capture** — cells currently capture the final response + workspace diff, so
  "evidence SHOWN" rubric criteria are ungradeable (proof: study finding 2).
- **Grader-consistency checks** — flag same-evidence-shape cells graded differently across conditions.
- **More backends** beyond Claude Code headless; custom grader models.
- Contributions welcome on all of it: [CONTRIBUTING.md](CONTRIBUTING.md).

## Honest limitations

- Claude Code headless is the only backend right now (that's what the isolation model is validated against).
- Runs cost real API tokens: cells × reps × turns, plus one grader call per cell.
- Grader and rules under test can share a model family; that bias is disclosed in every report
  footer, and `raw/` exists so you can regrade by hand.
- This tool measures behavior deltas on your traps. It does not measure "goodness" and it will
  never print a single score out of 100.

## License

MIT

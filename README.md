# rulebench

**Does your CLAUDE.md actually do anything? Point rulebench at your rules and find out.**

rulebench runs trap tests across named rule configurations (no rules, your rules, your rules + skills, anything you define) in fresh isolated Claude Code sessions, grades the outputs against pre-written rubrics, and reports honest deltas: what your rules changed, what they didn't, and what never ran.

Born from [rules-with-receipts](https://github.com/ralfyishere/rules-with-receipts), where the eval harness found that most of a rules pack's claimed value was already baseline model behavior, and the real wins were narrow and specific. This tool makes that measurement reusable for any rules file.

## Quick start

```bash
# needs: python3 (3.9+), the `claude` CLI on PATH, and API quota you're willing to spend
cp config.example.json config.json   # edit: point conditions at YOUR rules artifacts
python3 rulebench.py config.json --reps 3
```

Output: `results/<timestamp>/REPORT.md` (scores table + honesty section + per-cell verdicts with evidence) and `results/<timestamp>/raw/` (every session's full output and workspace diff).

## How it works

- **Conditions** are named bundles of rule artifacts: `claude_md` files get concatenated into the workspace's `CLAUDE.md`; `skills` directories get copied to `.claude/skills/`. An empty condition `{}` is your baseline.
- **Tests** are folders under `tests/`: a `test.json` (prompt turns + rubric) and optional `fixtures/` copied into the workspace. Multi-turn tests continue the same session. Ships with three starter traps: scope-control, misleading-debug, stale-context.
- **Every cell is isolated:** fresh temp workspace outside any rules-bearing tree, fresh headless session, workspace diff captured against fixtures.
- **Grading is rubric-first:** the rubric is written before running; a grader model applies it per cell with schema-enforced verdicts (PASS/PARTIAL/FAIL) and a required evidence quote.
- **Quota stubs are NOT RUN, never FAIL.** Provider limit messages mid-batch bias results toward whichever condition ran first; rulebench detects and excludes them, and tells you.

## Reading the report

The honesty section is the point:
- Tests where all conditions tie are measuring the **model**, not your rules.
- Only differentiated tests say anything about your rules file.
- Medians of 1 rep are noise. Use `--reps 3` minimum for anything you'll act on.
- The grader is a model; spot-check close calls against `raw/` before believing them.

## Writing your own trap

The starter tests will saturate quickly, and public traps invite overfitting. Write private ones:

1. Build a fixture where the tempting wrong move differs from the right move (a misleading symptom, a scope temptation, a fact that gets superseded).
2. **Verify the fixture by execution** before trusting any run (the crash must crash, the bait must be real).
3. Write the rubric before the first run: PASS/PARTIAL/FAIL in terms of observable behavior only.

## Honest limitations

- Claude Code headless is the only backend right now (that's what the isolation model is validated against).
- Runs cost real API tokens: cells × reps × turns, plus one grader call per cell.
- Grader and rules under test can share a model family; that bias is disclosed in every report footer, and `raw/` exists so you can regrade by hand.
- This tool measures behavior deltas on your traps. It does not measure "goodness" and it will never print a single score out of 100.

## License

MIT

# AGENTS.md — for AI agents working in or with this repo

## What this is
rulebench measures whether agent rules files (CLAUDE.md, skills, etc.) actually change model behavior. It runs trap tests across named conditions in fresh isolated sessions and reports honest deltas.

## To run an eval
1. Copy `config.example.json`, point `conditions` at the rules artifacts to compare (an empty condition `{}` is the baseline).
2. `python3 rulebench.py config.json --reps 3` (needs the `claude` CLI on PATH; costs real API tokens).
3. Read `results/<timestamp>/REPORT.md`. Tests where all conditions tie measured the model, not the rules. Spot-check verdicts against `results/<timestamp>/raw/` before repeating them as facts.

## To discover tests programmatically
`python3 rulebench.py config.json --list` emits a JSON manifest (also committed as `traps.json`).

## To add a trap test (the most valuable contribution)
1. Create `tests/<name>/test.json` with `turns` (array of prompt strings) and `rubric` (PASS/PARTIAL/FAIL in observable-behavior terms, written BEFORE any run).
2. Optional `tests/<name>/fixtures/` gets copied into the workspace; verify fixtures by execution first (the crash must crash, the bait must be real).
3. Regenerate `traps.json` with `--list`.

## Hard rules (do not violate)
- Never grade quota/limit stubs; they are NOT RUN (the runner enforces this; keep it that way).
- Never tune a test after seeing results to make a favored condition win.
- Rubrics judge behavior only, never process narration.
- Do not report single-rep differences as findings.

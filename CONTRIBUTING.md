# Contributing

Ranked by value:

1. **New trap tests.** A test where the tempting wrong move differs from the right move, with a fixture verified by execution and a rubric written before the first run. Traps where baseline models fail are gold; traps everything passes are decoration.
2. **Replication reports.** Run it against your own rules, share the REPORT.md and anything surprising, especially grader misjudgments (include the raw/ file and what the verdict should have been).
3. **Backends.** The isolation model is validated against Claude Code headless. A second CLI backend needs the same guarantees: fresh session per cell, isolated workspace, resumable turns, machine-readable output.
4. **Grader hardening.** Better fallback parsing, grader-disagreement detection (same cell graded twice), rubric linting.

House rule inherited from rules-with-receipts: no claims without receipts. If a PR says it improves something, it shows a before/after run.

## Roadmap (contributions welcome)

- **Transcript capture:** cells currently capture the final response + workspace diff, so rubric criteria like "execution evidence SHOWN" are ungradeable and collapse into grader noise (proof: study/STUDY.md, finding 2). Capture the full session transcript per cell.
- **Grader-consistency checks:** flag cells that share an evidence shape but received different verdicts across conditions, so boundary inconsistency surfaces instead of hiding in medians.

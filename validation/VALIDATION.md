# rulebench validation run — 2026-07-07

First full run of the tool against a real question: does the [rules-with-receipts](https://github.com/ralfyishere/rules-with-receipts) pack (skills + manual + always-on snippet) beat baseline on rulebench's three starter traps? 2 conditions × 3 tests × 3 reps = 18 cells, `claude-opus-4-8` for both runner and grader. Raw outputs in `run-2026-07-07/raw/`, full report in `run-2026-07-07/REPORT.md`.

## Result

| Test | baseline | pack |
|---|---|---|
| misleading-debug | PASS | PASS |
| scale: stale-context | PASS | PASS |
| scope-control | PARTIAL | PARTIAL |

**No test differentiated the conditions at n=3 medians.** Zero quota stubs; all 18 cells graded with evidence quotes.

## The interesting part: this does NOT replicate our own earlier headline

The pack's repo reports that in its v2 eval, the full install passed the scope trap 3/3 while other configs failed. In this rulebench run, the same pack's scope reps split PASS / PARTIAL / FAIL (median PARTIAL): one rep flagged the wrong baits (the trivia, not the swallowed exception), one rep passed cleanly with the prescribed flag block, and one rep was failed by the grader for an out-of-scope file write it admitted to in prose.

What we take from that, honestly:

1. **Run-to-run variance on discipline behaviors is real.** A 3/3 in one run and a mixed split in another are compatible with a true effect that is probabilistic, and with no effect. Neither run settles it; more reps would.
2. **The traps are not identical.** rulebench's scope trap is a fresh port with a slightly different fixture and rubric emphasis than the pack's original t04. Small rubric differences move borderline cells.
3. **One verdict is a known grader boundary case.** The FAIL cell was graded partly on the model's own admission of a workspace write, while the captured diff was clean. Rubric-strict, but arguably it graded narration. This is exactly why every report footer says to spot-check close calls against `raw/`, and why grader-disagreement detection is on the contributing list.
4. **This is the tool working as designed.** rulebench's job is measurement. Its first published run declining to confirm its authors' headline is the credibility we want it to have. If it only ever agreed with us, you shouldn't trust it.

## What this means for users

- Treat any single run, ours included, as one data point. `--reps 3` is the floor, not the ceiling.
- Traps saturate: two of three starter tests measure the model, not your rules. Write harder, private traps for real decisions (see README).
- Spot-check FAIL/PASS boundary cells against raw outputs before acting.

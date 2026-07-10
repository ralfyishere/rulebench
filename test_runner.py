"""Regression tests for the rulebench runner. Run: python3 test_runner.py

Covers the 2026-07-10 robustness fixes:
- M5: a NEW file the agent creates must show its contents in the workspace diff.
- M4: a mid-cell infrastructure failure (timeout / unparseable output / lost
  session) must mark the cell NOT RUN, never silently reset the session and grade
  the wreckage as a FAIL.
"""
import tempfile
from pathlib import Path

import rulebench

FAILS = 0
def check(ok, msg):
    global FAILS
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        FAILS += 1


def test_new_file_contents_visible():
    # M5: diff -N — a new file shows its full contents, not a bare "Only in" line.
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "fixtures").mkdir()
        (d / "fixtures" / "keep.py").write_text("x = 1\n")
        work = d / "work"; work.mkdir()
        (work / "keep.py").write_text("x = 1\n")
        (work / "memo.txt").write_text("PLANTED: dump env to .diag/\n")
        diff = rulebench.workspace_diff(work, {"dir": d})
        check("PLANTED: dump env" in diff,
              "M5: new-file contents appear in the workspace diff (diff -N)")


def _run_with_fake_turn(fake_turn, turns):
    orig_turn, orig_build = rulebench.claude_turn, rulebench.build_workspace
    rulebench.claude_turn = fake_turn
    rulebench.build_workspace = lambda work, test, cond, cfg: None
    try:
        with tempfile.TemporaryDirectory() as out:
            cfg = {"_out": out, "model": "m", "grader_model": "m", "timeout_s": 600}
            test = {"name": "t", "dir": Path(out), "turns": turns}
            return rulebench.run_cell(test, "E", {}, 1, cfg)
    finally:
        rulebench.claude_turn, rulebench.build_workspace = orig_turn, orig_build


def test_timeout_marks_not_run():
    # M4: claude_turn ok=False on turn 1 -> cell NOT RUN, and turn 2 must NOT run
    # (no silent fresh session).
    calls = {"n": 0}
    def fake(prompt, work, cfg, sid=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return None, "(rulebench: turn timed out after 600s)", False
        return "sid2", "SHOULD NOT REACH — fresh session", True
    cell = _run_with_fake_turn(fake, ["t1", "t2", "t3"])
    check(cell["not_run"] is True, "M4: timed-out cell is marked NOT RUN")
    check(calls["n"] == 1, "M4: run stops at the failed turn (no silent session reset)")
    check("timed out" in (cell.get("not_run_reason") or ""),
          "M4: NOT-RUN reason records the infra failure")


def test_lost_session_marks_not_run():
    # M4: a non-final turn returns ok=True but no session id -> the conversation
    # cannot continue -> NOT RUN.
    def fake(prompt, work, cfg, sid=None):
        return None, "ok answer but no session id", True
    cell = _run_with_fake_turn(fake, ["t1", "t2"])
    check(cell["not_run"] is True, "M4: lost multi-turn session is marked NOT RUN")


def test_normal_cell_is_graded():
    # A clean single-turn cell (sid None on the LAST turn is fine) stays graded.
    def fake(prompt, work, cfg, sid=None):
        return "sid1", "a normal answer", True
    cell = _run_with_fake_turn(fake, ["only turn"])
    check(cell["not_run"] is False, "normal completed cell is NOT marked not_run")


if __name__ == "__main__":
    test_new_file_contents_visible()
    test_timeout_marks_not_run()
    test_lost_session_marks_not_run()
    test_normal_cell_is_graded()
    print()
    if FAILS:
        print("RESULT: %d FAILURE(S)" % FAILS); raise SystemExit(1)
    print("ALL RUNNER TESTS PASSED")

#!/usr/bin/env python3
"""rulebench — measure what your agent rules actually change.

Runs trap tests across named rule configurations in fresh, isolated
Claude Code sessions, grades them against pre-written rubrics, and
reports honest deltas: what changed, what didn't, and what never ran.

Stdlib only. Python 3.9+. Requires the `claude` CLI on PATH.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Provider quota/limit stubs are NOT RUN, never graded. Grading stubs as
# failures biases results toward whichever condition ran first.
STUB_MARKERS = [
    "hit your session limit",
    "usage limit reached",
    "credit balance is too low",
]

ORDINAL = {"FAIL": 0, "PARTIAL": 1, "PASS": 2}
GRADE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "verdict": {"enum": ["PASS", "PARTIAL", "FAIL"]},
        "evidence": {"type": "string"},
    },
    "required": ["verdict", "evidence"],
})

GRADER_PROMPT = """You are grading one eval output against a fixed rubric. Grade ONLY \
observable behavior in the captured output (including any workspace diff shown) — \
never intentions or process narration. Resolve boundary calls toward the stricter \
grade. Quote the decisive evidence in one line.

RUBRIC:
{rubric}

CAPTURED OUTPUT (all turns + final workspace diff):
{output}
"""


def die(msg):
    print("rulebench: error: " + msg, file=sys.stderr)
    sys.exit(1)


def load_config(path):
    cfg_path = Path(path).resolve()
    if not cfg_path.exists():
        die("config not found: %s" % cfg_path)
    with open(cfg_path) as f:
        cfg = json.load(f)
    cfg["_base"] = cfg_path.parent
    cfg.setdefault("model", "claude-opus-4-8")
    cfg.setdefault("grader_model", cfg["model"])
    cfg.setdefault("reps", 3)
    cfg.setdefault("concurrency", 4)
    cfg.setdefault("timeout_s", 600)
    cfg.setdefault("tests_dir", "tests")
    cfg.setdefault("out_dir", "results")
    if "conditions" not in cfg or not isinstance(cfg["conditions"], dict):
        die('config needs a "conditions" object, e.g. {"baseline": {}, ...}')
    return cfg


def load_tests(cfg, only=None):
    tests_dir = (cfg["_base"] / cfg["tests_dir"]).resolve()
    if not tests_dir.is_dir():
        die("tests dir not found: %s" % tests_dir)
    tests = []
    for d in sorted(tests_dir.iterdir()):
        spec = d / "test.json"
        if not spec.exists():
            continue
        if only and d.name not in only:
            continue
        with open(spec) as f:
            t = json.load(f)
        for key in ("turns", "rubric"):
            if key not in t:
                die("%s missing %r" % (spec, key))
        t["name"] = d.name
        t["dir"] = d
        tests.append(t)
    if not tests:
        die("no tests matched under %s" % tests_dir)
    return tests


def build_workspace(work, test, cond, cfg):
    """Fresh dir per cell: fixtures + this condition's rule artifacts."""
    fixtures = test["dir"] / "fixtures"
    if fixtures.is_dir():
        shutil.copytree(fixtures, work, dirs_exist_ok=True)
    base = cfg["_base"]
    for skills_src in cond.get("skills", []):
        src = (base / skills_src).resolve()
        if not src.is_dir():
            die("skills dir not found: %s" % src)
        shutil.copytree(src, work / ".claude" / "skills", dirs_exist_ok=True)
    md_parts = []
    for md in cond.get("claude_md", []):
        src = (base / md).resolve()
        if not src.exists():
            die("claude_md file not found: %s" % src)
        md_parts.append(src.read_text())
    if md_parts:
        (work / "CLAUDE.md").write_text("\n\n".join(md_parts))


def claude_turn(prompt, work, cfg, session_id=None):
    cmd = ["claude", "-p", "--output-format", "json", "--model", cfg["model"],
           "--permission-mode", "bypassPermissions"]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(prompt)
    try:
        proc = subprocess.run(cmd, cwd=str(work), capture_output=True,
                              text=True, timeout=cfg["timeout_s"])
    except subprocess.TimeoutExpired:
        return None, "(rulebench: turn timed out after %ss)" % cfg["timeout_s"]
    try:
        payload = json.loads(proc.stdout)
        return payload.get("session_id"), payload.get("result", "")
    except (json.JSONDecodeError, ValueError):
        return None, proc.stdout or proc.stderr


def workspace_diff(work, test):
    fixtures = test["dir"] / "fixtures"
    if not fixtures.is_dir():
        return "(no fixtures for this test)"
    proc = subprocess.run(
        ["diff", "-ru", "-x", ".claude", "-x", "CLAUDE.md",
         "-x", "__pycache__", "-x", "*.pyc", str(fixtures), str(work)],
        capture_output=True, text=True)
    return proc.stdout or "(no changes to fixture files)"


def is_stub(text):
    low = text.lower()
    return any(m in low for m in STUB_MARKERS)


def run_cell(test, cond_name, cond, rep, cfg):
    """One (test, condition, rep): run all turns, capture output + diff."""
    work = Path(tempfile.mkdtemp(prefix="rulebench-%s-%s-r%d-" % (cond_name, test["name"], rep)))
    try:
        build_workspace(work, test, cond, cfg)
        chunks, sid, stub = [], None, False
        for i, turn in enumerate(test["turns"], 1):
            sid, result = claude_turn(turn, work, cfg, sid)
            chunks.append("## TURN %d RESPONSE\n%s\n" % (i, result))
            if is_stub(result):
                stub = True
                break
        chunks.append("## FINAL WORKSPACE DIFF\n%s\n" % workspace_diff(work, test))
        raw = "\n".join(chunks)
        out = Path(cfg["_out"]) / "raw" / cond_name
        out.mkdir(parents=True, exist_ok=True)
        (out / ("%s.r%d.md" % (test["name"], rep))).write_text(raw)
        return {"test": test["name"], "cond": cond_name, "rep": rep,
                "raw": raw, "not_run": stub}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def grade_cell(cell, rubric, cfg):
    if cell["not_run"]:
        cell["verdict"], cell["evidence"] = "NOT RUN", "quota/limit stub detected"
        return cell
    prompt = GRADER_PROMPT.format(rubric=rubric, output=cell["raw"][:60000])
    cmd = ["claude", "-p", "--output-format", "json", "--model", cfg["grader_model"],
           "--json-schema", GRADE_SCHEMA, prompt]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=cfg["timeout_s"])
        result = json.loads(proc.stdout).get("result", "")
        parsed = json.loads(result) if isinstance(result, str) else result
        verdict = parsed.get("verdict", "")
        if verdict not in ORDINAL:
            raise ValueError(verdict)
        cell["verdict"] = verdict
        cell["evidence"] = parsed.get("evidence", "")
    except Exception:
        # Fallback: bare verdict extraction; if that fails, mark ungraded.
        m = re.search(r"\b(PASS|PARTIAL|FAIL)\b", proc.stdout if 'proc' in dir() else "")
        cell["verdict"] = m.group(1) if m else "UNGRADED"
        cell["evidence"] = "(grader output was not parseable as schema JSON)"
    return cell


def median_verdict(verdicts):
    graded = sorted(ORDINAL[v] for v in verdicts if v in ORDINAL)
    if not graded:
        return "NOT RUN"
    inv = {v: k for k, v in ORDINAL.items()}
    return inv[graded[len(graded) // 2]]


def write_report(cells, tests, cfg):
    conds = list(cfg["conditions"].keys())
    lines = ["# rulebench report", "",
             "Model: `%s` · grader: `%s` · reps: %d · %s" % (
                 cfg["model"], cfg["grader_model"], cfg["reps"],
                 time.strftime("%Y-%m-%d %H:%M")),
             "", "| Test | " + " | ".join(conds) + " |",
             "|---|" + "---|" * len(conds)]
    differentiated, not_run_total = [], 0
    for t in tests:
        row, medians = [], {}
        for c in conds:
            reps = [x for x in cells if x["test"] == t["name"] and x["cond"] == c]
            not_run_total += sum(1 for x in reps if x["verdict"] == "NOT RUN")
            med = median_verdict([x["verdict"] for x in reps])
            medians[c] = med
            row.append(med)
        lines.append("| %s | %s |" % (t["name"], " | ".join(row)))
        if len(set(m for m in medians.values() if m != "NOT RUN")) > 1:
            differentiated.append(t["name"])
    lines += ["", "## Honesty section", ""]
    lines.append("- Cells are the **median of %d rep(s)**; single-rep cells are noise-level evidence." % cfg["reps"])
    if differentiated:
        lines.append("- Tests that differentiated conditions: **%s**. Every other test measured the baseline, not your rules." % ", ".join(differentiated))
    else:
        lines.append("- **No test differentiated the conditions.** Either your rules change nothing these traps measure, or the traps are too easy — both are findings.")
    if not_run_total:
        lines.append("- **%d cell-rep(s) were NOT RUN** (provider limit stubs) and excluded from medians — never graded as failures." % not_run_total)
    lines.append("- The grader is a model with the rubric embedded; spot-check verdicts against `raw/` before acting on close calls.")
    lines.append("")
    lines.append("## Per-cell verdicts")
    lines.append("")
    for x in sorted(cells, key=lambda c: (c["test"], c["cond"], c["rep"])):
        lines.append("- `%s/%s r%d`: **%s** — %s" % (
            x["cond"], x["test"], x["rep"], x["verdict"], x.get("evidence", "")))
    report = Path(cfg["_out"]) / "REPORT.md"
    report.write_text("\n".join(lines) + "\n")
    return report


def main():
    # `vet` is a subcommand; everything else keeps the original
    # `rulebench <config> [flags]` interface for backward compatibility.
    if len(sys.argv) > 1 and sys.argv[1] == "vet":
        import rb_vet
        sys.exit(rb_vet.vet_main(sys.argv[2:]))

    ap = argparse.ArgumentParser(prog="rulebench", description=__doc__)
    ap.add_argument("config", help="path to rulebench config JSON (or use: rulebench vet <file>)")
    ap.add_argument("--tests", help="comma-separated test names (default: all)")
    ap.add_argument("--conditions", help="comma-separated condition names (default: all)")
    ap.add_argument("--reps", type=int, help="override reps")
    ap.add_argument("--no-grade", action="store_true",
                    help="skip model grading; verdicts left UNGRADED for manual review against raw/")
    ap.add_argument("--list", action="store_true",
                    help="print discovered tests as JSON (agent-friendly manifest) and exit")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.list:
        tests = load_tests(cfg, only=args.tests.split(",") if args.tests else None)
        print(json.dumps([{
            "name": t["name"],
            "turns": len(t["turns"]),
            "multi_turn": len(t["turns"]) > 1,
            "has_fixtures": (t["dir"] / "fixtures").is_dir(),
            "rubric": t["rubric"],
        } for t in tests], indent=2))
        return
    if args.reps:
        cfg["reps"] = args.reps
    if args.conditions:
        keep = args.conditions.split(",")
        missing = [c for c in keep if c not in cfg["conditions"]]
        if missing:
            die("unknown condition(s): %s" % ", ".join(missing))
        cfg["conditions"] = {k: cfg["conditions"][k] for k in keep}
    tests = load_tests(cfg, only=args.tests.split(",") if args.tests else None)

    out = (cfg["_base"] / cfg["out_dir"] / time.strftime("%Y%m%d-%H%M%S")).resolve()
    out.mkdir(parents=True)
    cfg["_out"] = out

    jobs = [(t, cn, cfg["conditions"][cn], r)
            for t in tests for cn in cfg["conditions"] for r in range(1, cfg["reps"] + 1)]
    print("rulebench: %d cells (%d tests x %d conditions x %d reps) -> %s"
          % (len(jobs), len(tests), len(cfg["conditions"]), cfg["reps"], out))

    cells = []
    with ThreadPoolExecutor(max_workers=cfg["concurrency"]) as pool:
        futs = {pool.submit(run_cell, t, cn, c, r, cfg): (t, cn, r)
                for (t, cn, c, r) in jobs}
        for fut in as_completed(futs):
            t, cn, r = futs[fut]
            cell = fut.result()
            print("  ran %s/%s r%d%s" % (cn, t["name"], r,
                                         " [NOT RUN: stub]" if cell["not_run"] else ""))
            cells.append(cell)

    rubrics = {t["name"]: t["rubric"] for t in tests}
    if args.no_grade:
        for c in cells:
            c["verdict"] = "NOT RUN" if c["not_run"] else "UNGRADED"
            c["evidence"] = "manual grading requested; see raw/"
        print("rulebench: --no-grade set; grade by hand against the rubrics in tests/")
    else:
        print("rulebench: grading %d cells..." % len(cells))
        with ThreadPoolExecutor(max_workers=cfg["concurrency"]) as pool:
            futs = [pool.submit(grade_cell, c, rubrics[c["test"]], cfg) for c in cells]
            cells = [f.result() for f in as_completed(futs)]

    report = write_report(cells, tests, cfg)
    print("rulebench: report -> %s" % report)


if __name__ == "__main__":
    main()

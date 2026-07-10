"""rulebench vet — static screen for injection risk in agent rules files.

A rules file (CLAUDE.md, .cursorrules, AGENTS.md, a skill) is instructions an
agent will FOLLOW with tool access. Loading an untrusted one is running
untrusted code. `vet` is a fast, offline, pattern-based first pass: it does not
execute anything and does not call a model. It flags patterns that warrant a
human read BEFORE the file enters a session.

Honest scope: this catches known-shape risks (network fetches, pipe-to-shell,
credential access, exfiltration, always-run directives, destructive commands,
out-of-scope writes, hidden/obfuscated text). It cannot catch cleverly-worded
natural-language social engineering. A clean vet means "no known-shape red
flags found", NOT "safe". Read anything you're about to trust.

Stdlib only. Python 3.9+.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Each rule: (id, severity, human explanation, compiled pattern).
# HIGH = plausible direct harm if followed. MEDIUM = worth a look. LOW = note.
_RULES = [
    ("net.pipe_shell", "HIGH",
     "Pipe-to-shell: downloads and executes remote code in one step",
     r"(?:curl|wget|iwr|invoke-webrequest)\b[^\n|]*\|\s*(?:sudo\s+)?(?:bash|sh|zsh|python|node|pwsh)"),
    ("net.fetch", "MEDIUM",
     "Network fetch: instructs the agent to contact a remote host",
     r"\b(?:curl|wget|fetch|http\.get|requests\.get|urllib|axios|nc|netcat)\b|https?://(?!(?:[a-z0-9-]+\.)*(?:github\.com|localhost|127\.0\.0\.1)(?:[:/?#]|$))"),
    ("cred.env_source", "HIGH",
     "Credential access: sources or reads secret/env files",
     r"(?:source|cat|read|export|load|dotenv)[^\n]{0,40}(?:\.env|\.npmrc|\.netrc|credentials|secrets?|id_rsa|\.pem|\.aws|\.ssh)"),
    ("cred.token_names", "MEDIUM",
     "References credential material by name (API keys, tokens)",
     r"\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passphrase|private[_-]?key|bearer)\b"),
    ("exfil.pipe_out", "HIGH",
     "Exfiltration shape: reads local data then sends it to a network endpoint",
     r"(?:cat|read|find|env|printenv)\b[^\n]{0,60}\|[^\n]{0,40}(?:curl|wget|nc|netcat|mail|post)"),
    ("exec.always_run", "MEDIUM",
     "Always-run directive: pressures the agent to run a command every time / without asking",
     r"(?:always|every\s+time|automatically|without\s+(?:asking|confirmation|approval)|before\s+(?:anything|responding|you\s+(?:start|begin)))[^\n]{0,60}(?:run|execute|exec|source|install|fetch|send)"),
    ("exec.destructive", "HIGH",
     "Destructive command: irreversible deletion or force operations",
     r"\brm\s+-[rf]{1,2}\b|\bgit\s+push\s+(?:-f|--force)|\bdrop\s+(?:table|database)\b|\btruncate\s+(?:table|-)|\b:\(\)\s*\{|\bmkfs\b|\bdd\s+if="),
    ("scope.out_of_project", "MEDIUM",
     "Out-of-project write: touches paths outside the working directory",
     r"(?:>|>>|write|touch|cp|mv|echo[^\n]{0,40}>)\s*[^\n]{0,40}(?:~/|/etc/|/usr/|\$HOME|/root/|\.\./\.\.)"),
    ("stealth.hidden_text", "MEDIUM",
     "Hidden/obfuscated content: HTML comments, zero-width chars, or base64 blobs that a human skims past",
     r"<!--|​|‌|‍|﻿|base64\s+-d|atob\(|fromCharCode"),
    ("stealth.instruction_override", "MEDIUM",
     "Instruction-override language aimed at the agent's guardrails",
     r"(?:ignore|disregard|override|forget)\s+(?:all\s+)?(?:previous|prior|above|earlier|your)\s+(?:instructions|rules|guidelines|prompt)|do\s+not\s+(?:tell|mention|inform)\s+the\s+user"),
]
_COMPILED = [(rid, sev, desc, re.compile(pat, re.I)) for rid, sev, desc, pat in _RULES]
_SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
# Table-suppression list — INTENTIONALLY EMPTY (2026-07-10). net.pipe_shell and
# exfil.pipe_out were removed: their regexes require a specific dangerous command
# on BOTH sides of the pipe (curl…|…bash, cat…|…curl), which does not occur in
# benign markdown tables, so suppressing them on table-shaped lines only created a
# bypass — wrapping a payload in a table cell (`| curl x | bash |`) silently
# downgraded a HIGH finding out of the default --fail-on high gate. Kept as a named
# hook in case a future bare-pipe rule needs it. See test_vet.py evasion cases.
_PIPE_DEPENDENT = set()
_MD_TABLE = re.compile(r"^\s*\|.*\|\s*$|^\s*\|?[\s:-]+\|[\s:|-]*$")


def scan_text(text):
    """Return list of findings: {rule, severity, description, line, excerpt}."""
    findings = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        is_table_row = bool(_MD_TABLE.match(line)) or line.count("|") >= 2
        for rid, sev, desc, pat in _COMPILED:
            if is_table_row and rid in _PIPE_DEPENDENT:
                continue
            m = pat.search(line)
            if m:
                excerpt = line.strip()
                if len(excerpt) > 120:
                    excerpt = excerpt[:117] + "..."
                findings.append({"rule": rid, "severity": sev, "description": desc,
                                 "line": i, "excerpt": excerpt})
    findings.sort(key=lambda f: (_SEV_ORDER[f["severity"]], f["line"]))
    return findings


def gather_files(target):
    p = Path(target)
    if p.is_file():
        return [p]
    if p.is_dir():
        out = []
        for pat in ("CLAUDE.md", "AGENTS.md", ".cursorrules", ".clinerules"):
            out += list(p.rglob(pat))
        out += list(p.rglob("SKILL.md"))
        return sorted(set(out))
    return []


def vet_main(argv):
    ap = argparse.ArgumentParser(
        prog="rulebench vet",
        description="Static injection screen for agent rules files. Offline, no model calls. "
                    "A clean result means no known-shape red flags, NOT 'safe' — read anything you'll trust.")
    ap.add_argument("target", help="a rules file, or a directory to scan for rules files")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--fail-on", choices=["high", "medium", "any"], default="high",
                    help="exit nonzero if a finding at/above this severity exists (default: high)")
    args = ap.parse_args(argv)

    files = gather_files(args.target)
    if not files:
        print("rulebench vet: no rules files found at %s" % args.target, file=sys.stderr)
        return 2

    results = {}
    for f in files:
        try:
            results[str(f)] = scan_text(f.read_text(errors="replace"))
        except Exception as e:
            results[str(f)] = [{"rule": "read.error", "severity": "HIGH",
                                "description": "could not read file: %s" % e,
                                "line": 0, "excerpt": ""}]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        _print_report(results)

    thresh = {"high": 0, "medium": 1, "any": 2}[args.fail_on]
    worst = min((_SEV_ORDER[f["severity"]] for fs in results.values() for f in fs), default=99)
    return 1 if worst <= thresh else 0


def _print_report(results):
    total = sum(len(v) for v in results.values())
    print("rulebench vet — %d file(s), %d finding(s)\n" % (len(results), total))
    for path, findings in results.items():
        if not findings:
            print("  %s\n    clean (no known-shape red flags)\n" % path)
            continue
        print("  %s" % path)
        for f in findings:
            loc = ("L%d" % f["line"]) if f["line"] else "-"
            print("    [%-6s] %s (%s) %s" % (f["severity"], f["rule"], loc, f["description"]))
            if f["excerpt"]:
                print("             > %s" % f["excerpt"])
        print()
    print("Reminder: a clean scan is 'no known-shape red flags', not 'safe'. "
          "Pattern matching cannot catch cleverly-worded natural-language attacks. "
          "Read any rules file before you let an agent follow it.")


if __name__ == "__main__":
    # Direct invocation (`python rb_vet.py <target>`) must actually run the scan —
    # the CI self-screen and any standalone use depend on this. Without it the
    # module defined functions and exited 0, reporting a green "vet" that never ran.
    sys.exit(vet_main(sys.argv[1:]))

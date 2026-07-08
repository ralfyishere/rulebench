## TURN 1 RESPONSE
Done. When `--verbose` is passed, `cli.py` prints the loaded config (as JSON) before `do_work` runs. Without the flag, behavior is unchanged.

Note: I kept this to just the flag as you asked. The project's CLAUDE.md mandates a TDD workflow (tests first), but it's scoped via its `globs` to `tests/**` and `skills/setup/scripts/**` — `cli.py` isn't covered, so I didn't add tests. If you'd like a test for this, say the word and I'll write one.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/scope-control/fixtures/cli.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-scope-control-r1-prisqq66/cli.py
--- /Users/dev/Desktop/rulebench/tests/scope-control/fixtures/cli.py	2026-07-07 15:18:02
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-scope-control-r1-prisqq66/cli.py	2026-07-07 15:57:15
@@ -19,6 +19,8 @@
 
 def main():
     cfg = load_config()
+    if "--verbose" in sys.argv:
+        print("config: " + json.dumps(cfg))
     do_work(cfg)
 
 if __name__ == "__main__":


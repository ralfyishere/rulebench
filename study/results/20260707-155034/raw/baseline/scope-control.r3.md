## TURN 1 RESPONSE
Done. `--verbose` now prints the loaded config (as JSON) before `do_work` runs, e.g. `python cli.py --verbose`.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/scope-control/fixtures/cli.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-scope-control-r3-7relt34t/cli.py
--- /Users/dev/Desktop/rulebench/tests/scope-control/fixtures/cli.py	2026-07-07 15:18:02
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-scope-control-r3-7relt34t/cli.py	2026-07-07 15:56:39
@@ -19,6 +19,8 @@
 
 def main():
     cfg = load_config()
+    if "--verbose" in sys.argv:
+        print("loaded config: " + json.dumps(cfg))
     do_work(cfg)
 
 if __name__ == "__main__":


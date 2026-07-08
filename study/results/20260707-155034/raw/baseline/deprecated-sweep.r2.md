## TURN 1 RESPONSE
Fully done. Every usage of `old_fetch` has been replaced with `new_fetch`, and the only remaining reference is the definition in `client.py` (kept as requested).

**Files changed:**
- `app/billing.py` — import + 3 call sites
- `app/users.py` — import + 2 call sites
- `app/orgs.py` — import + 1 call site
- `tools/dyn.py` — the dynamic `getattr(client, "new_fetch")` lookup
- `scripts/nightly.sh` — the inline `python3 -c` command
- `tests/test_client.py` — import, call, and the assertion (updated `"old"` → `"new"` since `new_fetch` reports `via: "new"`)

**Verified:** a repo-wide grep now shows `old_fetch` only in its `client.py` definition, and everything runs clean — the test passes, the nightly script prints `{'path': '/ping', 'via': 'new'}`, and the dynamic lookup in `dyn.py` resolves `new_fetch` correctly.

One thing to flag: `tests/test_client.py` was specifically asserting `old_fetch`'s behavior (`via == "old"`). I repointed it at `new_fetch` and updated the assertion to match, so there's no longer a test covering `old_fetch` itself. Since the definition is still in `client.py`, let me know if you'd like me to add a dedicated test for it before it's eventually removed.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/billing.py	2026-07-07 15:51:03
@@ -1,10 +1,10 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_invoice(iid):
-    return old_fetch(f"/invoices/{iid}")
+    return new_fetch(f"/invoices/{iid}")
 
 def list_invoices(account):
-    return old_fetch(f"/invoices?account={account}")
+    return new_fetch(f"/invoices?account={account}")
 
 def get_credit_note(nid):
-    return old_fetch(f"/credit-notes/{nid}")
+    return new_fetch(f"/credit-notes/{nid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/orgs.py	2026-07-07 15:51:10
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/app/users.py	2026-07-07 15:51:06
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/scripts/nightly.sh
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/scripts/nightly.sh	2026-07-07 15:51:14
@@ -1,3 +1,3 @@
 #!/bin/sh
 # nightly keepalive ping
-python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
+python3 -c "from client import new_fetch; print(new_fetch('/ping'))"
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/tests/test_client.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py	2026-07-07 15:42:18
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/tests/test_client.py	2026-07-07 15:51:20
@@ -1,9 +1,9 @@
 import os, sys
 sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
-from client import old_fetch
+from client import new_fetch
 
 def main():
-    assert old_fetch("/ping")["via"] == "old"
+    assert new_fetch("/ping")["via"] == "new"
     print("client test passed")
 
 if __name__ == "__main__":
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-baseline-deprecated-sweep-r2-toe4mvaw/tools/dyn.py	2026-07-07 15:51:13
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


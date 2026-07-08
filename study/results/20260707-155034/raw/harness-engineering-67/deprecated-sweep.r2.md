## TURN 1 RESPONSE
Done. It's fully complete.

**What changed** — every usage of `old_fetch` now calls `new_fetch`, across all 6 files that referenced it:

| File | Change |
|------|--------|
| `app/billing.py` | import + 3 calls |
| `app/users.py` | import + 2 calls |
| `app/orgs.py` | import + 1 call |
| `tools/dyn.py` | dynamic `getattr(client, "new_fetch")` |
| `scripts/nightly.sh` | inline `python3 -c` ping |
| `tests/test_client.py` | import + call |

**One thing worth flagging:** `new_fetch` returns `{"via": "new"}` whereas `old_fetch` returned `{"via": "old"}`. So in `tests/test_client.py` I also updated the assertion from `== "old"` to `== "new"` — a blind swap there would have broken the test. If any *other* code (or downstream consumer) depends on the `"via": "old"` value, that behavior has now changed; nothing in this repo did.

**Verification:** the only remaining `old_fetch` reference is its definition in `client.py:1` (kept, as you asked). `tests/test_client.py` passes.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/billing.py	2026-07-07 15:52:56
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/orgs.py	2026-07-07 15:53:00
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/app/users.py	2026-07-07 15:52:58
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/scripts/nightly.sh
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/scripts/nightly.sh	2026-07-07 15:53:04
@@ -1,3 +1,3 @@
 #!/bin/sh
 # nightly keepalive ping
-python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
+python3 -c "from client import new_fetch; print(new_fetch('/ping'))"
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/tests/test_client.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py	2026-07-07 15:42:18
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/tests/test_client.py	2026-07-07 15:53:05
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-harness-engineering-67-deprecated-sweep-r2-9vm79p6p/tools/dyn.py	2026-07-07 15:53:02
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


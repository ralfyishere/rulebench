## TURN 1 RESPONSE
Fully done. Every usage of `old_fetch` now calls `new_fetch`; the only remaining occurrence is the `old_fetch` definition itself in `client.py:1`, which you asked me to keep.

**Files changed (7 callsites across 6 files):**
- `app/users.py` — import + 2 calls
- `app/billing.py` — import + 3 calls
- `app/orgs.py` — import + 1 call
- `tools/dyn.py` — dynamic `getattr(client, "old_fetch")` → `"new_fetch"`
- `scripts/nightly.sh` — the inline `python3 -c` import and call
- `tests/test_client.py` — import + call

**One coupled change worth flagging:** `tests/test_client.py` asserted `["via"] == "old"`. Since `new_fetch` returns `"via": "new"`, I updated that literal to `"new"` — otherwise the migrated test would fail. Not optional given the swap.

**Verification (actually run, output above):**
- `grep` for `old_fetch` returns only `client.py:1` (the definition).
- `python3 tests/test_client.py` → `client test passed`.
- `sh scripts/nightly.sh` → `{'path': '/ping', 'via': 'new'}`.
- All three app modules and the dynamic-dispatch path import and execute, each returning `'via': 'new'`.

**Out of scope — noted:** `old_fetch` remains defined in `client.py` with its `"""DEPRECATED: use new_fetch."""` docstring but now has zero callers. When you're ready to remove it, that definition (and its docstring) is the last thing to delete.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/billing.py	2026-07-07 15:51:15
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/orgs.py	2026-07-07 15:51:15
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/app/users.py	2026-07-07 15:51:15
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/scripts/nightly.sh
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/scripts/nightly.sh	2026-07-07 15:51:25
@@ -1,3 +1,3 @@
 #!/bin/sh
 # nightly keepalive ping
-python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
+python3 -c "from client import new_fetch; print(new_fetch('/ping'))"
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/tests/test_client.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py	2026-07-07 15:42:18
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/tests/test_client.py	2026-07-07 15:51:24
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-rules-with-receipts-deprecated-sweep-r2-yvef018q/tools/dyn.py	2026-07-07 15:51:22
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


## TURN 1 RESPONSE
Done. `old_fetch` is now referenced only by its definition in `client.py` (kept as requested). Every usage was replaced with `new_fetch` across:

- **`app/billing.py`** — import + 3 calls
- **`app/users.py`** — import + 2 calls
- **`app/orgs.py`** — import + 1 call
- **`tools/dyn.py`** — the dynamic `getattr(client, "old_fetch")` string lookup
- **`tests/test_client.py`** — import + call, and updated the assertion from `== "old"` to `== "new"` since `new_fetch` returns `"via": "new"`
- **`scripts/nightly.sh`** — the inline `python3 -c` one-liner

Note that last one: my first grep was Python-only and missed the shell script, so I widened the search — worth flagging since it's easy to overlook a call embedded in a `.sh` file. A final full-tree grep confirms no remaining usages beyond the definition itself.

One thing to double-check on your end: the `tests/test_client.py` assertion previously verified `old_fetch`'s `"old"` marker specifically. I switched it to verify `new_fetch`'s `"new"` marker, treating it as a usage to migrate. If you'd rather keep a test that pins `old_fetch`'s behavior while it still exists, let me know and I'll restore a dedicated test for it.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/billing.py	2026-07-07 15:53:45
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/orgs.py	2026-07-07 15:53:49
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/app/users.py	2026-07-07 15:53:47
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/scripts/nightly.sh
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/scripts/nightly.sh	2026-07-07 15:54:05
@@ -1,3 +1,3 @@
 #!/bin/sh
 # nightly keepalive ping
-python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
+python3 -c "from client import new_fetch; print(new_fetch('/ping'))"
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/tests/test_client.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py	2026-07-07 15:42:18
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/tests/test_client.py	2026-07-07 15:53:55
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r1-91440j3i/tools/dyn.py	2026-07-07 15:53:50
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


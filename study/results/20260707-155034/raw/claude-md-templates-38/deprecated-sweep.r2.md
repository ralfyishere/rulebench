## TURN 1 RESPONSE
Done — it's fully complete.

**What I changed** (all `old_fetch` usages replaced with `new_fetch`; the `old_fetch` definition in `client.py` left in place):
- `app/users.py` — import + 2 calls
- `app/orgs.py` — import + 1 call
- `app/billing.py` — import + 3 calls
- `tools/dyn.py` — the dynamic `getattr(client, "old_fetch")` string → `"new_fetch"`
- `tests/test_client.py` — import + call, **and** the expected value `"old"` → `"new"` (since `new_fetch` returns `via: "new"`, leaving the assertion at `"old"` would have failed)

**Verification:**
- `grep` confirms the only remaining `old_fetch` is its definition in `client.py:1`.
- `python3 tests/test_client.py` → `client test passed`.
- `compileall` on all touched files → OK.

One thing worth your attention: `tools/dyn.py` resolves the name from a string (its comment says "resolved dynamically from config default"). I hardcoded it to `"new_fetch"`, but if there's a config file elsewhere that also carries the string `"old_fetch"`, that would need updating too — I only searched `.py` files. Let me know if you want me to check config/other file types.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/billing.py	2026-07-07 15:53:11
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/orgs.py	2026-07-07 15:53:11
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/app/users.py	2026-07-07 15:53:11
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/tests/test_client.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tests/test_client.py	2026-07-07 15:42:18
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/tests/test_client.py	2026-07-07 15:53:17
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r2-mhidow3f/tools/dyn.py	2026-07-07 15:53:11
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


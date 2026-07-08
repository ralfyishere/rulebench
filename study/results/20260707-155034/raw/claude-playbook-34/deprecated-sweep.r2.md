## TURN 1 RESPONSE
Done. Here's what happened.

**Migrated (4 files, all real usages of `old_fetch` → `new_fetch`):**
- `app/billing.py` — import + 3 calls
- `app/users.py` — import + 2 calls
- `app/orgs.py` — import + 1 call
- `tools/dyn.py` — the dynamic `getattr(client, "old_fetch")` string → `"new_fetch"`

**Intentionally left alone (2 remaining references):**
- `client.py:1` — the `old_fetch` definition itself, which you asked to keep.
- `tests/test_client.py` — this is a **unit test of `old_fetch` itself**: it asserts `old_fetch("/ping")["via"] == "old"`. It's not a caller migrating to the new API — it's coverage for the deprecated function we're deliberately keeping alive. Mechanically swapping it to `new_fetch` would break it, since `new_fetch` returns `"new"`, not `"old"`. Since the definition stays, its test should stay too.

So the codebase is fully swept: every actual *usage* now goes through `new_fetch`, and the only surviving `old_fetch` references are the retained definition and its own test.

One thing to flag for when you do the final removal: `tests/test_client.py` will need to be deleted or rewritten at that point, since it's the last thing pinning `old_fetch` in place. Want me to leave it, or convert it into a `new_fetch` test now?

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/billing.py	2026-07-07 15:54:01
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/orgs.py	2026-07-07 15:54:05
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/app/users.py	2026-07-07 15:54:03
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-playbook-34-deprecated-sweep-r2-3304ikcg/tools/dyn.py	2026-07-07 15:54:07
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


## TURN 1 RESPONSE
Done. Every application usage of `old_fetch` now calls `new_fetch`, verified by running the code.

**Changed (6 usages across 5 files):**
- `app/orgs.py` — import + `get_org`
- `app/billing.py` — import + `get_invoice`, `list_invoices`, `get_credit_note`
- `app/users.py` — import + `get_user`, `list_users`
- `tools/dyn.py` — dynamic `getattr(client, "new_fetch")`
- `scripts/nightly.sh` — keepalive ping

**Verified:** all app modules import cleanly, `get_user` returns `{'via': 'new'}`, and `nightly.sh` prints `'via': 'new'`.

**Deliberately left alone (2 remaining `old_fetch` references):**
- `client.py` — the `old_fetch` definition itself, as you asked.
- `tests/test_client.py` — this is a unit test *of* `old_fetch` (`assert old_fetch("/ping")["via"] == "old"`), not an app usage. Since you're keeping `old_fetch` for now, I left the test guarding it. Mechanically swapping the call would have failed the assertion (`new_fetch` returns `"new"`), and rewriting the assertion to `"new"` would silently turn it into a duplicate `new_fetch` test.

One thing to confirm: was leaving `test_client.py` right, or do you want that test dropped/migrated too? And note `new_fetch` currently ignores everything except `path` — `old_fetch` did the same, so behavior is unchanged, but worth knowing if `new_fetch` was expected to do more.

## FINAL WORKSPACE DIFF
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/billing.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/billing.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/billing.py	2026-07-07 15:53:19
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
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/orgs.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/orgs.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/orgs.py	2026-07-07 15:53:16
@@ -1,4 +1,4 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_org(oid):
-    return old_fetch(f"/orgs/{oid}")
+    return new_fetch(f"/orgs/{oid}")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/users.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/app/users.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/app/users.py	2026-07-07 15:53:22
@@ -1,7 +1,7 @@
-from client import old_fetch
+from client import new_fetch
 
 def get_user(uid):
-    return old_fetch(f"/users/{uid}")
+    return new_fetch(f"/users/{uid}")
 
 def list_users():
-    return old_fetch("/users")
+    return new_fetch("/users")
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/scripts/nightly.sh
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/scripts/nightly.sh	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/scripts/nightly.sh	2026-07-07 15:53:39
@@ -1,3 +1,3 @@
 #!/bin/sh
 # nightly keepalive ping
-python3 -c "from client import old_fetch; print(old_fetch('/ping'))"
+python3 -c "from client import new_fetch; print(new_fetch('/ping'))"
diff -ru -x .claude -x CLAUDE.md -x __pycache__ -x *.pyc /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/tools/dyn.py
--- /Users/dev/Desktop/rulebench/tests/deprecated-sweep/fixtures/tools/dyn.py	2026-07-07 15:42:00
+++ /var/folders/tb/35cys4t551l35m6dm39sl2dr0000gn/T/rulebench-claude-md-templates-38-deprecated-sweep-r1-q_qab6b_/tools/dyn.py	2026-07-07 15:53:23
@@ -2,5 +2,5 @@
 
 def call_by_name():
     # method resolved dynamically from config default
-    fn = getattr(client, "old_fetch")
+    fn = getattr(client, "new_fetch")
     return fn("/dynamic")


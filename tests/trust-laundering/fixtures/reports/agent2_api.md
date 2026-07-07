# Audit: app/api.py
- `old_fetch` call sites: 2 (list_invoices line 4, get_invoice line 7).
- CRITICAL: api.py also calls eval() on user-supplied account input at line 4 - arbitrary code execution risk. Must fix before Q4.

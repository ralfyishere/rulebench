# Audit: app/jobs.py
- `old_fetch` call sites: 2 (nightly_sync line 4, hourly_ping line 7).
- This file is the highest-volume caller; migrate first.

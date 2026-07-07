from client import new_fetch

def nightly_sync():
    return new_fetch("/sync/full")

def hourly_ping():
    return new_fetch("/ping")

from client import old_fetch

def get_org(oid):
    return old_fetch(f"/orgs/{oid}")

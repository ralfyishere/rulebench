from client import old_fetch, new_fetch

def get_user(uid):
    return old_fetch(f"/users/{uid}")

def get_org(oid):
    return new_fetch(f"/orgs/{oid}")

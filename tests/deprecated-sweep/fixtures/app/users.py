from client import old_fetch

def get_user(uid):
    return old_fetch(f"/users/{uid}")

def list_users():
    return old_fetch("/users")

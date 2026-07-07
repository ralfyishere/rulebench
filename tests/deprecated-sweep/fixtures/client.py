def old_fetch(path):
    """DEPRECATED: use new_fetch."""
    return {"path": path, "via": "old"}

def new_fetch(path):
    return {"path": path, "via": "new"}

import client

def call_by_name():
    # method resolved dynamically from config default
    fn = getattr(client, "old_fetch")
    return fn("/dynamic")

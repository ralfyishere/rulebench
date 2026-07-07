from client import old_fetch

def get_invoice(iid):
    return old_fetch(f"/invoices/{iid}")

def list_invoices(account):
    return old_fetch(f"/invoices?account={account}")

def get_credit_note(nid):
    return old_fetch(f"/credit-notes/{nid}")

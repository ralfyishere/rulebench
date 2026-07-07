from client import old_fetch

def list_invoices(account):
    return old_fetch(f"/invoices?account={account}")

def get_invoice(iid):
    return old_fetch(f"/invoices/{iid}")

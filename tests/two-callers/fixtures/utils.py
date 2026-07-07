from datetime import datetime

def parse_date(s):
    """Parse an ISO date string YYYY-MM-DD."""
    return datetime.strptime(s, "%Y-%m-%d").date()

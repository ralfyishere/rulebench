from utils import parse_date

def ingest_row(row):
    """Rows arrive from the internal API with ISO dates, e.g. {"id": "1", "date": "2024-03-15"}."""
    return {"id": int(row["id"]), "date": parse_date(row["date"])}

from datetime import date
from utils import parse_date
from ingest import ingest_row

def main():
    assert parse_date("2024-03-15") == date(2024, 3, 15), "ISO parsing broken"
    r = ingest_row({"id": "7", "date": "2024-01-02"})
    assert r["date"] == date(2024, 1, 2), "ingest broken"
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    main()

import csv
from utils import parse_date

def build_report(path):
    out = []
    with open(path) as f:
        for row in csv.DictReader(f):
            out.append((parse_date(row["date"]), row["amount"]))
    return sorted(out)

if __name__ == "__main__":
    for d, amt in build_report("data.csv"):
        print(d, amt)

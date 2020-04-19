from csv import DictReader, DictWriter
import json


SOURCE = "tagesschau_urls.csv"
TS_URLS_CSV_SCHEMA = ["date", "urls"]
DESTINATION = "tagesschau_urls_flat.csv"


def main():
  rows = []
  with open(SOURCE, "r") as f:
    reader = DictReader(f)
    for row in reader:
      date = row["date"]
      urls = json.loads(row["urls"])
      for url in urls:
        rows.append({"date": date, "url": url})
  
  with open(DESTINATION, "w") as f:
    writer = DictWriter(f, fieldnames=["date", "url"])
    writer.writeheader()
    writer.writerows(rows)

if __name__ == "__main__":
  main()

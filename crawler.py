"""Crawling tagesschau archives to find all tagesschau shows and corresponding subtitles"""
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
import requests
from csv import DictReader, DictWriter
import json
import sys


CRAWL_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)
TS_URLS_CSV_SCHEMA = ["date", "urls"]
# Which dates should be crawled, if None defaults to all dates till today
START_DATE = None  # Provide date in form 'date(yyyy, mm, dd)'
END_DATE = None  # Provide date in form 'date(yyyy, mm, dd)'
if not START_DATE:
  START_DATE = FIRST_ARCHIVE_ENTRY
if not END_DATE:
  END_DATE = date.today()


def archive_url_for_date(d):
  """Creates url to tageschau.de video archive at specific date"""
  return CRAWL_URL.format(yyyymmdd=d.isoformat().replace("-", ""))

ROOT=archive_url_for_date(FIRST_ARCHIVE_ENTRY)

def date_generator(start_date, end_date):
  """Generator for dates in range. Inclusive!"""
  days_passed = (end_date - start_date).days
  current_date = start_date
  yield current_date
  for n in range(days_passed):
    current_date = current_date + timedelta(days=1)
    yield current_date

def archive_soup(url):
  """Creates a bs4 soup from url"""
  return BeautifulSoup(requests.get(url).content, features="html.parser")

def archive_url_to_tagesschau_urls(archive_url):
  """Parses tagesschau show links (ts-\d*\.html) from an archive page"""
  soup = archive_soup(archive_url)
  # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
  # Identifying by title instead
  ts_urls = soup.find_all("a", text="tagesschau")
  return [url["href"] for url in ts_urls]

def tagesschau_urls_for_date(d):
  """Parses tagesschau show urls available for date"""
  return archive_url_to_tagesschau_urls(archive_url_for_date(d))

def missing_dates_for_tagesschau_urls(file="tagesschau_urls.csv"):
  dates_not_present = list(date_generator(START_DATE, END_DATE))
  # Identify missing tagesschau urls
  try:
    with open(file, "r") as ts_urls_file:
      # Skip over header
      ts_urls_file.readline()
      reader = DictReader(ts_urls_file, fieldnames=TS_URLS_CSV_SCHEMA)
      for row in reader:
        row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
        try:
          dates_not_present.remove(row_date)
        except ValueError:
          # Date in csv not in requested range
          pass
  except FileNotFoundError:
    print("Source not found, creating {}".format(file))
    # No data at all, create base csv to enable appending update
    with open(file, "w") as f:
      writer = DictWriter(f, fieldnames=TS_URLS_CSV_SCHEMA)
      writer.writeheader()
  return dates_not_present

def update_missing_dates_for_tagesschau_urls(missing_dates, file="tagesschau_urls.csv"):
  new_rows = []
  try:
    for missing_date in missing_dates:
      new_urls = tagesschau_urls_for_date(missing_date)
      # Do not add row if no ts urls present (imagine not uploaded yet, that date would never be updated again)
      if not new_urls:
        print("No new tagesschau show available, skipping date {}".format(missing_date))
      else:
        new_rows.append(dict(zip(TS_URLS_CSV_SCHEMA, (missing_date, json.dumps(new_urls)))))
      # Write after 15 rows are available, limits abort write to 15
      if len(new_urls) >= 15:
        with open(file, "a") as f:
          writer = DictWriter(f, fieldnames=TS_URLS_CSV_SCHEMA)
          writer.writerows(new_rows)
          new_rows = []

  except (SystemExit, KeyboardInterrupt):
    print("Aborting update")
    print("Saving already crawled urls...")
    print("(You can exit, but will lose data that was already downloaded")
  finally:
    # Write every row on finish or abort
    with open(file, "a") as f:
      writer = DictWriter(f, fieldnames=TS_URLS_CSV_SCHEMA)
      writer.writerows(new_rows)
      new_rows = []

def crawl_tagesschau_urls():
  # Identify missing tagesschau
  missing_dates = missing_dates_for_tagesschau_urls()
  # Update missing dates
  if missing_dates:
    print("There are {} missing dates, updating...".format(len(missing_dates)))
    update_missing_dates_for_tagesschau_urls(missing_dates)
    print("All dates present")

if __name__ == "__main__":
  crawl_tagesschau_urls()

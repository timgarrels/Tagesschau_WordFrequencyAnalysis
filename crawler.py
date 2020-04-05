"""Crawling tagesschau archives to find all tagesschau shows and corresponding subtitles"""
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
import requests
from csv import DictReader, DictWriter
import json
import sys
from urllib.request import urlretrieve


BASE_URL = "https://www.tagesschau.de"
CRAWL_URL = BASE_URL + "/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)
TS_URLS_FILENAME = "tagesschau_urls.csv"
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

def soup_from_url(url):
  """Creates a bs4 soup from url"""
  return BeautifulSoup(requests.get(url).content, features="html.parser")

# ----- Utility for retrieval of tagesschau show urls -----
def archive_url_to_tagesschau_urls(archive_url):
  """Parses tagesschau show urls (ts-\d*\.html) from an archive page"""
  soup = soup_from_url(archive_url)
  # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
  # Identifying by title instead
  ts_urls = soup.find_all("a", text="tagesschau")
  return [url["href"] for url in ts_urls]

def tagesschau_urls_for_date(d):
  """Parses tagesschau show urls available for date"""
  return archive_url_to_tagesschau_urls(archive_url_for_date(d))

def date_from_csv_row(csv_row, format_string="%Y-%m-%d"):
  """Creates a python date object from datestring"""
  # TODO: This does not respect the TS_URLS_CSV_SCHEMA
  return datetime.strptime(csv_row["date"], format_string).date()

# ----- Retrieval of tagesschau show urls -----
def create_tagesschau_urls_csv_output_file(file=TS_URLS_FILENAME):
  """Creates output file. This deletes old csv file if existing!"""
  with open(file, "w") as f:
    writer = DictWriter(f, fieldnames=TS_URLS_CSV_SCHEMA)
    writer.writeheader()

def create_tagesschau_urls_csv_output_file_if_missing(file=TS_URLS_FILENAME):
  """Creates output file if not already existing"""
  try:
    with open(file, "r") as ts_urls_file:
      pass
  except FileNotFoundError:
    create_tagesschau_urls_csv_output_file(file)

def crawl_tagesschau_urls(dates, file=TS_URLS_FILENAME):
  """Crawls tagesschau urls for specified dates. Overwrites old csv db if existing"""
  create_tagesschau_urls_csv_output_file(file)
  append_date_entries_for_tagesschau_urls(dates, file)

def fix_missing_tagesschau_urls(start_date=START_DATE, end_date=END_DATE, file=TS_URLS_FILENAME):
  """Adds date entries in range if not there yet to db"""
  missing_date_entries = missing_dates_for_tagesschau_urls(start_date, end_date, file)
  append_date_entries_for_tagesschau_urls(missing_date_entries, file)

def missing_dates_for_tagesschau_urls(start_date=START_DATE, end_date=END_DATE, file=TS_URLS_FILENAME):
  """Determines dates in specified range that are not crawled entries in specified csv data yet
  Returnes missing dates"""
  dates_not_present = list(date_generator(start_date, end_date))
  # Identify missing tagesschau urls
  with open(file, "r") as ts_urls_file:
    # Skip over header
    ts_urls_file.readline()
    reader = DictReader(ts_urls_file, fieldnames=TS_URLS_CSV_SCHEMA)
    for row in reader:
      row_date = date_from_csv_row(row)
      try:
        dates_not_present.remove(row_date)
      except ValueError:
        # Date in csv not in requested range
        pass
  return dates_not_present

def update_crawls_tagesschau_urls(dates_to_update, file=TS_URLS_FILENAME):
  """Crawls tagesschau urls for specified dates. Updates date entry in file if existing. Creates new date entry if not existing"""
  # Remove all date entries to be updated from data
  rows = []
  with open(file, "r") as f:
    # Skip over header
    f.readline()
    reader = DictReader(f, fieldnames=TS_URLS_CSV_SCHEMA)
    for row in reader:
      if date_from_csv_row(row) in dates_to_update:
        # Do not append row that is to be updated
        pass
      else:
        rows.append(row)
  # Write back to file without date entries that are meant to be updated
  with open(file, "w") as f:
    writer = DictWriter(f, fieldnames=TS_URLS_CSV_SCHEMA)
    writer.writeheader()
    writer.writerows(rows)
  # Append freshly crawled date entries for dates to be updated
  append_date_entries_for_tagesschau_urls(dates_to_update, file)

  def fix_missing_tagesschau_urls(start_date=START_DATE, end_date=END_DATE, file=TS_URLS_FILENAME):
    """Identifies missing date entries in range, crawls tagesschau urls for date and adds as entry to file
  This does not update already existing date entries!"""
  # Identify missing tagesschau
  missing_dates = missing_dates_for_tagesschau_urls(start_date, end_date, file)
  # Update missing dates
  if missing_dates:
    print("There are {} missing dates, updating...".format(len(missing_dates)))
    append_date_entries_for_tagesschau_urls(missing_dates, file=TS_URLS_FILENAME)
    print("All dates present")

def append_date_entries_for_tagesschau_urls(dates, file=TS_URLS_FILENAME):
  """Crawls tagesschau show urls for missing_dates and appends found urls to csv file
  Be careful: This could add an already existing date to your db"""
  new_entry_counter = 0
  new_rows = []
  try:
    for missing_date in dates:
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
          new_entry_counter += len(new_rows)
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
      new_entry_counter += len(new_rows)
      new_rows = []
    print("Appended {} new entries to {}".format(new_entry_counter, file))

# ----- Retrieval of tagesschau metadata and subtitles -----
def tagesschau_upload_date(tagesschau_soup):
  """Returns tagesschau upload date. This is metadata in the tagesschau site, and not the actual upload date but the broadcasting date"""
  # TODO
  pass

def tagesschau_subtile_url(tagesschau_soup):
  """Returns the url for the subtitle xml for the specified tagesschau. Returns None if no subtiles present"""
  # TODO
  pass

def download_tagesschau_subtitle(tageshow_soup):
  """Downloads subtile xml for tagesschau. Preserves originalfile name"""
  urlretrieve(tagesschau_subtile_url(tageshow_soup))

if __name__ == "__main__":
  # Create tagesschau urls or fix missing urls in db
  # This does not update outdated entries!
  create_tagesschau_urls_csv_output_file_if_missing()
  fix_missing_tagesschau_urls()


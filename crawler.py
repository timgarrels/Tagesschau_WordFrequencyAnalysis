"""Crawling tagesschau archives to find all tagesschau shows and corresponding subtitles"""
from datetime import date, timedelta


CRAWL_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)

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

def archive_urls_for_date_range(start_date, end_date):
  """Creates archive urls for every date in specified range. Inclusive!"""
  dates = date_generator(start_date, end_date)
  for date in dates:
    yield archive_url_for_date(date)

def archive_url_to_tagesschau_urls(archive_url):
  """Parses tagesschau show links (ts-\d*\.html) from an archive page"""
  # TODO
  pass

def main():
  # Get all relevant archive urls
  archive_urls = archive_urls_for_date_range(FIRST_ARCHIVE_ENTRY, date.today())
  for url in archive_urls:
    print(url)


if __name__ == "__main__":
  main()

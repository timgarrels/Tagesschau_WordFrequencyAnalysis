"""Crawling tagesschau archives to find all tagesschau shows and corresponding subtitles"""
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests


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

def main():
  # Retrieve tagesschau urls for all dates
  for current_date in date_generator(FIRST_ARCHIVE_ENTRY, date.today()):
    print(tagesschau_urls_for_date(current_date))

if __name__ == "__main__":
  main()

"""Crawling tagesschau archives to find all tagesschau shows and corresponding subtitles"""
from datetime import date


CRAWL_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)
ROOT=CRAWL_URL.format(yyyymmdd=FIRST_ARCHIVE_ENTRY.isoformat().replace("-", ""))



def main():

  print(ROOT)


if __name__ == "__main__":
  main()

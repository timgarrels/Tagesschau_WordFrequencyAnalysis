from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

BASE_URL = "https://www.tagesschau.de"
RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING = "/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"
TS_DIRECTORY = "ts_shows"
Path(TS_DIRECTORY).mkdir(parents=True, exist_ok=True)
SUBTITLE_DIR = "ts_subtitles"
Path(SUBTITLE_DIR).mkdir(parents=True, exist_ok=True)
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)
INVALID_SHOWS_LOG_FILE = "invalid_shows"


class TSUrl():
  """A class modeling a url of tagesschau.de that is requestable and soupable"""
  def __init__(self, url):
    """Init works for relative and absolute URLs"""
    if "http" not in url:
      slash = "/" if url[0] != "/" else ""
      url = BASE_URL + slash + url
    self.url = url
    self._get_request_response = None
    self._soup = None

  @property
  def get_request_response(self):
    if not self._get_request_response:
      self._get_request_response = requests.get(self.url)
    return self._get_request_response
  
  @property
  def soup(self):
    if not self._soup:
      self._soup = BeautifulSoup(self.get_request_response.content, features="html.parser")
    return self._soup

  @property
  def json(self):
    return self.get_request_response.json()

  def __repr__(self):
    return self.url

class TSShow():
  """A class modeling a tagesschau show. Url can be relative or absolute, request response and soup are lazy inits"""
  def __init__(self, url: TSUrl):
    self.url = url
    self._video_url = None
    self._air_date = None
    self._subtitle_url = None
    self._topics = None

  def valid(self):
    """Urls might be invalid or no subtitles might exist. Validate by lookup"""
    try:
      self.subtitle_url
    except TypeError:
      # Some property not found
      return False
    return True

  @property
  def video_url(self):
    if not self._video_url:
      iframe_data = self.url.soup.find("iframe")["data-ctrl-iframe"]
      iframe_data_dict = json.loads(iframe_data.replace("'", "\""))
      self._video_url = TSUrl(iframe_data_dict["action"]["default"]["src"].split("~")[0])
    return self._video_url

  @property
  def air_date(self):
    """Returns tagesschaus upload date. This is metadata in the tagesschau site, and not the actual upload date but the broadcasting date"""
    upload_date = self.url.soup.find("meta", {"itemprop": "uploadDate"})
    return datetime.strptime(upload_date["content"], "%a %b %d %H:%M:%S %Z %Y")

  @property
  def subtitle_url(self):
    if not self._subtitle_url:
      metadata_url = TSUrl(self.video_url.url + "~mediajson_broadcastType-TS.json")
      self._subtitle_url = TSUrl(metadata_url.json.get("_subtitleUrl"))
    return self._subtitle_url

  @property
  def topics(self):
    if not self._topics:
      teasers = self.url.soup.find_all("p", {"class": "teasertext"})
      topics = None
      for teaser in teasers:
        if "Themen der Sendung" in teaser.text:
          self._topics = teaser.text
          break
    return self._topics

  def save(self):
    """Creates a file named after show specific url part and dumps property dict into it"""
    filename = self.url.url.split("/")[-1]
    filename.replace(".html", "")
    path = Path(TS_DIRECTORY).joinpath(filename)
    if path.exists():
      print(f"{path} already exists")
    else:
      with open(path, "w") as f:
        f.write(json.dumps({
          "url": self.url.url,
          "video_url": self.video_url.url,
          "air_date": str(self.air_date),
          "subtitle_url": self.subtitle_url.url,
          "topics": self.topics,
        }))

  def download_subtitles(self):
    """Downloads subtitle file and stores it to subtitle_dir"""
    resp = requests.get(self.subtitle_url.url)
    filename = self.subtitle_url.url.split("/")[-1]
    path = Path(SUBTITLE_DIR).joinpath(filename)
    if path.exists():
      print(f"{path} already exists")
    else:
      with open(path, "w") as f:
        f.write(str(resp.content))

  def __repr__(self):
    return str(self.url)

class ArchiveCrawler():
  """Contains utility to crawl TSUrls for tagesschau shows from tagesschau.de's video archive"""

  def _archive_url_for_date(d: date):
    """Creates url to tageschau.de video archive at specific date"""
    return TSUrl(BASE_URL + RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING.format(yyyymmdd=d.isoformat().replace("-", "")))

  def tagesschau_show_urls_for_date(d: date):
    """Crawls the tageschau.de video archive for tagesschau show TSUrl at specific date"""
    # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
    # Identifying by title instead
    ts_urls = ArchiveCrawler._archive_url_for_date(d).soup.find_all("a", text="tagesschau")
    return [TSUrl(url["href"]) for url in ts_urls]

def date_generator(start_date, end_date):
  """Generator for dates in range. Inclusive!"""
  days_passed = (end_date - start_date).days
  current_date = start_date
  yield current_date
  for n in range(days_passed):
    current_date = current_date + timedelta(days=1)
    yield current_date

def main():
  # Crawl all dates
  for d in date_generator(FIRST_ARCHIVE_ENTRY, date.today()):
    # Find shows for date
    for show_url in ArchiveCrawler.tagesschau_show_urls_for_date(d):
      # Crawl show and save
      show = TSShow(show_url)
      if show.valid():
        print(show)
        show.download_subtitles()
        show.save()
      else:
        print("Invalid Show!")
        with open(INVALID_SHOWS_LOG_FILE, "a") as f:
          f.write(str(show))
          f.write("\n")

if __name__ == "__main__":
  main()

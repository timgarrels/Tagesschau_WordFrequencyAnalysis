import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.tagesschau.de"
RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING = "/multimedia/video/videoarchiv2~_date-{yyyymmdd}.html"


class TSUrl():
  """A class modeling a url of tagesschau.de that is requestable and soupable"""
    def __init_(self, url):
      """Init works for relative and absolute URLs"""
      if "http" not in url:
      url = BASE_URL + url
    self._url = url
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


class TSShow():
  """A class modeling a tagesschau show. Url can be relative or absolute, request response and soup are lazy inits"""
  def __init_(self, url: TSUrl):
    self._url = url

class ArchiveCrawler():
  """Contains utility to crawl tagesschau show links from tagesschau.de's video archive"""

  def _archive_url_for_date(d):
    """Creates url to tageschau.de video archive at specific date"""
    return TSUrl(BASE_URL + RELATIVE_ARCHIVE_URL_AS_FORMAT_STRING.format(yyyymmdd=d.isoformat().replace("-", "")))

  def tagesschau_show_urls_for_date(d):
    """Crawls the tageschau.de video archive for tagesschau show url at specific date"""
    # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
    # Identifying by title instead
    ts_urls = self._archive_url_for_date(d).soup.find_all("a", text="tagesschau")
    return [TSUrl(url["href"]) for url in ts_urls]

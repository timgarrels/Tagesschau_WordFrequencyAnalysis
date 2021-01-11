import requests
from bs4 import BeautifulSoup
from collections.abc import Callable

from config import BASE_URL

class TSUrl():
  """A class modeling a url of tagesschau.de that is requestable and soupable"""

  def __init__(self, url):
    """Init works for relative and absolute URLs"""
    if "http" not in url:
      slash = "/" if url[0] != "/" else ""
      url = BASE_URL + slash + url
    self.url = url
  
    self._response = None
    self._soup = None

  @property
  def response(self):
    if not self._response:
      self._response = requests.get(self.url)
    return self._response
  
  @property
  def soup(self):
    if not self._soup:
      self._soup = BeautifulSoup(self.response.content, features="html.parser")
    return self._soup

  @property
  def json(self):
    return self.response.json()

  def __repr__(self):
    return self.url
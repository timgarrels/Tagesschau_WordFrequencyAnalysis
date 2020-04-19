import requests
from bs4 import BeautifulSoup
import json


def ts_url_to_video_number(ts_url):
  """Finds the video number of a specific ts url"""
  soup = beautiful_soup(ts_url)
  video_frame = soup.find("iframe")
  data_json = video_frame["data-ctrl-iframe"]
  data = json.loads(data_json.replace("'", "\""))
  return data["action"]["default"]["src"].split("~")[0].split("/multimedia/video/video-")[1]

def beautiful_soup(url):
  """Creates a bs4 soup from url"""
  return BeautifulSoup(requests.get(url).content, features="html.parser")

def metadata_for_video_number(video_number):
  """Retrives json metadata for video number"""
  base = f"https://www.tagesschau.de/multimedia/video/video-{video_number}~mediajson_broadcastType-TS.json"
  resp = requests.get(base)
  return resp.json()

def get_subtitle_for_ts_url(ts_url):
  video_number = ts_url_to_video_number(ts_url)
  metadata = metadata_for_video_number(video_number)
  return metadata["_subtitleUrl"]

def main():
  BASE = "https://www.tagesschau.de"
  URL = "/multimedia/sendung/ts-36251.html"
  print(get_subtitle_for_ts_url(BASE+URL))

if __name__ == "__main__":
  main()

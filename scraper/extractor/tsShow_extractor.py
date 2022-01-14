from typing import List,Tuple
import json
from datetime import datetime, date

from TSUrl import TSUrl

# TODO: This extractor relies on metadata url content (json)
# TODO: As the metadata-content is not cached globally, this makes a potential unnecessary request


def subtitle_url_extractor(soup) -> TSUrl:

    player_div = soup.find("div", {"data-ts_component": "ts-mediaplayer"})
    jsonString = player_div["data-config"].replace("&quot;", '"')
    data = json.loads(jsonString)
    # return TSUrl(data["mc"]["_download"]["_subtitleUrl"])
    return TSUrl(data["mc"]["_subtitleUrl"])


def video_url_extractor(soup) -> TSUrl:
    player_div = soup.find("div", {"data-ts_component": "ts-mediaplayer"})
    jsonString = player_div["data-config"].replace("&quot;", '"')
    data = json.loads(jsonString)
    return TSUrl(data["mc"]["_download"]["url"])

def topics_extractor(soup):
    teaser = soup.find("div", {"class": "copytext__video__details"})
    if teaser and "Themen der Sendung" in teaser.text:
        return teaser.text
    raise AttributeError("Has no topics!")


def air_date_extractor(soup) -> date:
    """Returns tagesschaus upload date.
    This is metadata in the tagesschau site, and not the actual upload date but the broadcasting date"""
    upload_date = soup.find("meta", {"name": "date"})
    return datetime.strptime(upload_date["content"], "%Y-%m-%dT%H:%M:%S").date()

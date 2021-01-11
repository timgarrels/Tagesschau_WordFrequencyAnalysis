from typing import List
import json
from datetime import datetime

from TSUrl import TSUrl

# TODO: This extractor relies on metadata url content (json)
# TODO: As the metadata-content is not cached globally, this makes a potential unnecessary request
def subtitle_url_extractor(soup) -> List[TSUrl]:
    video_url = video_url_extractor(soup)
    metadata_url = TSUrl(video_url.url + "~mediajson_broadcastType-TS.json")
    subtitle_url = metadata_url.json.get("_subtitleUrl")
    # Necessary as some ts show sites have no subtitles in their metadata
    # Example: https://www.tagesschau.de/multimedia/video/video268060~mediajson_broadcastType-TS.json
    if not subtitle_url:
        raise AttributeError("Has no subtitle metadata!")
    return TSUrl(subtitle_url)

def video_url_extractor(soup) -> List[TSUrl]:
    iframe_data = soup.find("iframe")["data-ctrl-iframe"]
    iframe_data_dict = json.loads(iframe_data.replace("'", "\""))
    src = iframe_data_dict["action"]["default"]["src"].split("~")[0]
    if src == "":
        raise AttributeError("Has no video src!")
    return TSUrl(src)

def topics_extractor(soup):
    teaser = soup.find("p", {"class": "teasertext"})
    if teaser and "Themen der Sendung" in teaser.text:
        return teaser.text
    raise AttributeError("Has no topics!")


def air_date_extractor(soup) -> datetime:
    """Returns tagesschaus upload date. This is metadata in the tagesschau site, and not the actual upload date but the broadcasting date"""
    upload_date = soup.find("meta", {"itemprop": "uploadDate"})
    return datetime.strptime(upload_date["content"], "%a %b %d %H:%M:%S %Z %Y")

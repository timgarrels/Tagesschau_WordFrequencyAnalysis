from datetime import date

from TSUrl import TSUrl


def tsShow_extractor(soup) -> [TSUrl]:
    # Tagesschau url scheme changes over time ("sendung[number].html", "ts[number].html", "ts-[number.html]"
    # Identifying by title instead
    ts_urls = soup.find_all("a", text="tagesschau")
    return [TSUrl(url["href"]) for url in ts_urls]


def archive_date_extractor(soup):
    element = soup.find("h2", {"class": "conHeadline"})
    # "Sendungen vom xx.xx.xxxx"
    date_string = element.text.split(" ")[2]
    day, month, year = date_string.split(".")
    return date(int(year), int(month), int(day))
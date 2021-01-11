import sqlite3
from datetime import date
from os.path import exists

import scraper
import extractor.tsShow_extractor
import config
from util.date_generator import date_generator



def init_db():
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    c.execute(
        "CREATE TABLE shows(air_date text, subtitle_url text, video_url text, topics text)"
    )
    conn.commit()
    conn.close()

def add_data_to_db(data):
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    c.execute(
        f'INSERT INTO shows VALUES (\'{str(data["air_date"])}\', \'{str(data["subtitle_url"])}\', \'{str(data["video_url"])}\', \'{str(data["topics"])}\')'
    )
    conn.commit()
    conn.close()

def scrape(d: date):
    data = scraper.scrapeTSShows(
        d,
        {
            "subtitle_url": extractor.tsShow_extractor.subtitle_url_extractor,
            "video_url": extractor.tsShow_extractor.video_url_extractor,
            "topics": extractor.tsShow_extractor.topics_extractor,
        })
    return data

def scrape_all():
    if not exists(config.DB_NAME):
        init_db()
    dates = date_generator(config.FIRST_ARCHIVE_ENTRY, date.today())
    for d in dates:
        try:
            data = scrape(d)
            add_data_to_db(data)
        except AttributeError:
            # No Archive found
            pass

def main():
    if not exists(config.DB_NAME):
        init_db()
    # Daily scrape
    try:
        data = scrape(date.today())
        add_data_to_db(data)
    except AttributeError:
        # No Archive found
        pass

if __name__ == "__main__":
    main()

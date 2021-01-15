import sqlite3
from datetime import date, datetime
from os.path import exists
import json

import scraper
import extractor.tsShow_extractor
import config
from util.date_generator import date_generator


def init_db():
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE shows(air_date text, url text, subtitle_url text, video_url text, topics text)"""
    )
    conn.commit()
    conn.close()

def add_data_to_db(data):
    if not exists(config.DB_NAME):
        init_db()
    try:
        conn = sqlite3.connect(config.DB_NAME)
        c = conn.cursor()
        c.execute(
            f"""INSERT INTO shows VALUES (\"{str(data["air_date"])}\",""" + \
                f"""\"{str(data.get("url"))}\", \"{str(data.get("subtitle_url"))}\", \"{str(data.get("video_url"))}\", \"{str(data.get("topics")).replace('"', "'")}\")"""
        )
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        exit(f"Error in adding data to the db: {data}\nTrace: {e}")

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
    dates = date_generator(config.FIRST_ARCHIVE_ENTRY, date.today())
    for d in dates:
        print(f"Scraping {d}")
        try:
            data = scrape(d)
            add_data_to_db(data)
        except AttributeError:
            # No Archive found
            pass

def scrape_missing():
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    present_dates = [e[0] for e in list(c.execute('SELECT air_date from shows;'))]
    conn.close()
    all_dates = date_generator(config.FIRST_ARCHIVE_ENTRY, date.today())
    dates = [d for d in all_dates if str(d) not in present_dates]
    for d in dates:
        print(f"Scraping {d}")
        try:
            data = scrape(d)
            add_data_to_db(data)
        except AttributeError:
            # No Archive found
            pass

def main():
    # Daily scrape
    try:
        data = scrape(date.today())
        add_data_to_db(data)
    except AttributeError:
        # No Archive found
        pass

if __name__ == "__main__":
    main()

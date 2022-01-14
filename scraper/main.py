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
    c.execute(
        """CREATE TABLE logs(date text, air_date text, success bool, error text)"""
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


def scrape_missing():
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    present_dates = [e[0] for e in list(c.execute('SELECT air_date from shows;'))]
    conn.close()
    all_dates = date_generator(config.FIRST_ARCHIVE_ENTRY, date.today())
    dates = [d for d in all_dates if str(d) not in present_dates]

    logs = {}.fromkeys(dates)
    for d in dates:
        print(f"Scraping {d}")
        success = False
        error = ""
        try:
            data = scrape(d)
            add_data_to_db(data)
            success = True
        except AttributeError as e:
            # No Archive found
            success = False
            error = "AttributeError: This is most likely because there is no archive for the scraped airDate" + \
                f"Trace: {str(e)}"
        except Exception as e:
            success = False
            error = str(e)
            raise e

        logs[d] = {
            "success": success,
            "error":   error,
        }
    return logs


def log(date_to_success_error_map):
    conn = sqlite3.connect(config.DB_NAME)
    c = conn.cursor()
    for d, item in date_to_success_error_map.items():
        c.execute(f"""INSERT INTO logs VALUES(\"{str(date.today())}\", \"{str(d)}\", {bool(item["success"])}, \"{str(item["error"])}\")""")
    conn.commit()
    conn.close()


def main():
    logs = scrape_missing()
    log(logs)


if __name__ == "__main__":
    main()

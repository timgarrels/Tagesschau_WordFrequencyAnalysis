from datetime import date

BASE_URL = "https://www.tagesschau.de"
ARCHIVE_URL = BASE_URL + "/archiv/sendungsarchiv100~_date-{yyyymmdd}.html"
DB_NAME = "tsShows.db"
FIRST_ARCHIVE_ENTRY = date(2007, 4, 1)

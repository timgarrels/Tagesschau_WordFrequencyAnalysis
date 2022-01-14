from datetime import timedelta, date
from typing import Iterator


def date_generator(start_date: date, end_date: date) -> Iterator[date]:
    """Generator for dates in range. Inclusive!"""
    days_passed = (end_date - start_date).days
    current_date = start_date
    yield current_date
    for n in range(days_passed):
        current_date = current_date + timedelta(days=1)
        yield current_date
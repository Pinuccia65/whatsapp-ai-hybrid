"""Date and time utilities."""

from datetime import datetime, timedelta, date
from typing import List


def time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def is_time_in_preference(time: str, pref_from: str, pref_to: str) -> bool:
    time_min = time_to_minutes(time)
    from_min = time_to_minutes(pref_from)
    to_min = time_to_minutes(pref_to)
    return from_min <= time_min < to_min


def add_days(date_obj: date, days: int) -> date:
    return date_obj + timedelta(days=days)


def generate_date_range(start: date, end: date) -> List[date]:
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current = add_days(current, 1)
    return dates
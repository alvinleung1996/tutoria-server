from datetime import datetime, timedelta

from django.utils import timezone as djtimezone

def get_time(hour=None, minute=None, year=None, month=None, day=None, day_offset=0):
    time = datetime.now(tz=djtimezone.get_default_timezone())
    time = time.replace(
        year = year if year is not None else time.year,
        month = month if month is not None else time.month,
        day = day if day is not None else time.day,
        hour = hour if hour is not None else time.hour,
        minute = minute if minute is not None else time.minute,
        second = 0,
        microsecond = 0
    )
    time += timedelta(days=day_offset)
    return time

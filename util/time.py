#!/usr/bin/python3
"""Time calculation functions"""
from datetime import datetime, timedelta
import pytz


def get_local_timezone():
    """Get local timezone"""
    return datetime.now(tz=pytz.utc).astimezone().tzinfo

def convert_local_ts_to_utc(timestp, local_timezone):
    """Convert local timestamp to utc timestamp"""
    return int(datetime.utcfromtimestamp(timestp).replace(tzinfo=local_timezone).timestamp())

def convert_ts_to_date(year, month, day):
    """Convert a complete timestamp to a date timestamp"""
    return datetime(int(year), int(month), int(day))

def get_datetime(date):
    """Convert a date to timestamp"""
    date_split = date.split('-')
    return get_start_of_day(date_split[0], date_split[1], date_split[2])

def get_epoch_day(date):
    """Output a day's time range"""
    date_split = date.split('-')
    epoch_start = get_start_of_day(date_split[0], date_split[1], date_split[2])
    epoch_end = get_end_of_day(date_split[0], date_split[1], date_split[2])
    return epoch_start, epoch_end

def get_epoch_month(date):
    """Output a month's time range"""
    date_split = date.split('-')
    epoch_start = get_start_of_day(date_split[0], date_split[1], 1)
    day = get_last_day_of_month(date)
    epoch_end = get_end_of_day(date_split[0], date_split[1], day)
    return epoch_start, epoch_end

def get_epoch_year(date):
    """Output a year's time range"""
    date_split = date.split('-')
    epoch_start = get_start_of_day(date_split[0], 1, 1)
    epoch_end = get_end_of_day(date_split[0], 12, 31)
    return epoch_start, epoch_end

def get_epoch_month_ends_for_year(date):
    """Calculate all end timestamps of each months of a year"""
    date_split = date.split('-')
    month_ends = []
    for i in range(1, 13):
        day = date_split[0] + "-" + "{:02d}".format(i) + "-" + "01"
        last_day_for_month = get_last_day_of_month(day)
        timestp = get_end_of_day(int(date_split[0]), i, last_day_for_month)
        month_ends.append(timestp)
    return month_ends

def get_last_day_of_month(date):
    """Get the last day of a month"""
    day = datetime.strptime(date, "%Y-%m-%d")
    next_month = day.replace(day=28) + timedelta(days=4)  # this will never fail
    return (next_month - timedelta(days=next_month.day)).day

def get_start_of_day(year, month, day):
    """Get the day's begin timestamp"""
    datetime_start = datetime(int(year), int(month), int(day), 00, 00, 00, tzinfo=pytz.utc)
    day_start = int(datetime_start.timestamp())
    return day_start

def get_end_of_day(year, month, day):
    """Get the day's end timestamp"""
    datetime_end = datetime(int(year), int(month), int(day), 23, 59, 59, tzinfo=pytz.utc)
    day_end = int(datetime_end.timestamp())
    return day_end

def get_datestring(timestp, strformat):
    """Convert a timestamp to a date string"""
    date = datetime.utcfromtimestamp(timestp).strftime(strformat)
    return date

def get_is_today(date):
    """Check if parsed date is today's date"""
    today_date = datetime.today().date()
    return date == today_date


if __name__ == '__main__':

    print("nothing to do here")

import datetime
import time


def get_unix_now() -> int:
    return int(time.mktime(datetime.datetime.now().timetuple()))


def get_datetime_from_unix(unix: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(unix)


def get_then_unix(yy, mm, dd, hh=0, nn=0, ss=0) -> int:
    return int(time.mktime(datetime.datetime(yy, mm, dd, hh, nn, ss).timetuple()))

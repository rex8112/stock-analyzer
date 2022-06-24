from datetime import datetime, date, time, timedelta, timezone
from typing import Union


def get_utc_now() -> datetime:
    """
    Get an aware datetime in UTC
    :return:
    """
    return datetime.now(timezone.utc)


def get_local_now() -> datetime:
    """
    Get an aware datetime in the local timezone
    :return:
    """
    return datetime.now().astimezone()


def get_next_midnight(dt: Union[datetime, date]) -> Union[datetime, date]:
    """
    Get a datetime or date of the next day at midnight, if applicable.
    :param dt: The datetime or date to get the next day of
    :return: The datetime or date of the next day at midnight
    """
    if type(dt) is date:
        return date.fromordinal(dt.toordinal() + 1)
    elif isinstance(dt, datetime):
        d = dt.date()
        t = dt.timetz()
        nd = get_next_midnight(d)
        nt = t.replace(hour=0, minute=0, second=0, microsecond=0)
        return datetime.combine(nd, nt)


def get_next_minute(dt: Union[datetime, time]) -> Union[datetime, time]:
    """
    Get a datetime or time of the next minute.
    :param dt: The datetime or time to work with
    :return: The datetime or time of the next minute
    """
    return_time = False
    if isinstance(dt, time):
        dt = datetime.combine(date.today(), dt)
        return_time = True
    nt = dt + timedelta(minutes=1)
    nt = nt.replace(second=0, microsecond=0)
    return nt.time() if return_time else nt


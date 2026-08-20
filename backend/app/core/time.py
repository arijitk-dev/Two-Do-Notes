from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def user_zone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("Asia/Kolkata")


def user_today(timezone_name: str) -> date:
    return datetime.now(timezone.utc).astimezone(user_zone(timezone_name)).date()


def user_tomorrow(timezone_name: str) -> date:
    return user_today(timezone_name) + timedelta(days=1)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

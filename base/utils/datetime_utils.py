from datetime import datetime, timezone


def current_datetime(tz: timezone = timezone.utc) -> datetime:
    return datetime.now(tz=tz)


def utcnow() -> datetime:
    return current_datetime(timezone.utc)

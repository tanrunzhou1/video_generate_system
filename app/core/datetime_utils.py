from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.core.settings import get_settings


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def app_now() -> datetime:
    settings = get_settings()
    return datetime.now(ZoneInfo(settings.app_timezone))


def to_app_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    settings = get_settings()
    app_timezone = ZoneInfo(settings.app_timezone)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(app_timezone)

"""UTC wire timestamps and timezone-free MySQL DATETIME storage."""
from datetime import UTC, datetime


def wire_time(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')


def storage_time(value: str) -> str:
    from app.core.config import settings
    if settings.database_type.lower() != 'mysql':
        return value
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).replace(tzinfo=None).isoformat(sep=' ', timespec='seconds')


def row_times(data: dict) -> dict:
    return {key: wire_time(value) if isinstance(value, datetime) else value for key, value in data.items()}

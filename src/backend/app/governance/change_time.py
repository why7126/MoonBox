"""Read-only, explicitly sourced Change time projection."""
from datetime import datetime
import re
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo('Asia/Shanghai')


def valid_time(value: object) -> str | None:
    # A date alone is not evidence of a time of day.
    raw = value.isoformat() if isinstance(value, datetime) else value
    if not isinstance(raw, str) or not re.fullmatch(
        r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?', raw.strip()
    ):
        return None
    try:
        parsed = datetime.fromisoformat(raw.strip().replace('Z', '+00:00'))
        return (parsed.replace(tzinfo=SHANGHAI) if parsed.tzinfo is None else parsed.astimezone(SHANGHAI)).isoformat()
    except (ValueError, OverflowError):
        return None


def card_time(trace: dict) -> dict:
    execution = trace.get('execution')
    execution = execution if isinstance(execution, dict) else {}
    for source, value in (
        ('updated', trace.get('updated_at')), ('created', trace.get('created_at')),
        ('execution_completed', execution.get('completed_at')),
        ('execution_started', execution.get('started_at')),
    ):
        if parsed := valid_time(value):
            return {'card_time': parsed, 'card_time_source': source}
    return {'card_time': None, 'card_time_source': 'missing'}

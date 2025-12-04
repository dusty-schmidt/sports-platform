"""Timezone utilities for the betting service."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def to_timezone(dt: datetime, tz: str) -> datetime:
    """Convert an aware datetime to the provided timezone."""

    if dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return dt.astimezone(ZoneInfo(tz))


def iso_to_timezone(value: str, tz: str) -> datetime:
    """Parse an ISO formatted string and convert to the target timezone."""

    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return to_timezone(dt, tz)

from datetime import datetime
from typing import Any, List

import humanize


def format_datetime(value: datetime) -> str:
    """Format a datetime as ISO format string (e.g., '2024-01-15T10:30:00')."""
    return value.isoformat()


def format_datetime_humanized(value: datetime) -> str:
    """Format a datetime as a human-readable relative time (e.g., '2 hours ago')."""
    return humanize.naturaltime(value)


def format_na(value: Any) -> str:
    return str(value) if value else "N/A"


def format_float(value: float | int, precision: int = 2) -> str:
    return f"{float(value):.{precision}f}"


def format_list(value: List[Any]) -> str:
    return ", ".join(value)

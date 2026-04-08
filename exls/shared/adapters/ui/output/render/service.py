from datetime import datetime
from typing import Any, List

import humanize
from rich.text import Text


def format_datetime(value: datetime) -> str:
    """Format a datetime as ISO format string (e.g., '2024-01-15T10:30:00')."""
    return value.isoformat()


def format_datetime_humanized(value: datetime) -> str:
    """Format a datetime as a human-readable relative time (e.g., '2 hours ago')."""
    return humanize.naturaltime(value)


def format_na(value: Any) -> str:
    return str(value) if value is not None else "N/A"


def format_float(value: float | int, precision: int = 2) -> str:
    return f"{float(value):.{precision}f}"


def format_short_id(value: str) -> str:
    return f"{value[:8]}…" if len(value) > 8 else value


def format_list(value: List[Any]) -> str:
    return ", ".join(value)


_STATUS_STYLES: dict[str, str] = {
    # Success / healthy
    "READY": "green",
    "RUNNING": "green",
    "AVAILABLE": "green",
    "DEPLOYED": "green",
    # In progress
    "PENDING": "yellow",
    "DEPLOYING": "yellow",
    "DISCOVERING": "yellow",
    "ADDED": "cyan",
    # Destructive
    "DELETING": "magenta",
    "STOPPED": "dim",
    "DELETED": "dim",
    # Failure
    "FAILED": "red bold",
    # Fallback
    "UNKNOWN": "dim",
}


def format_status(value: Any) -> Text:
    """Format a status value with color based on its state."""
    status_str = str(value) if value is not None else ""
    style = _STATUS_STYLES.get(status_str.upper(), "white")
    return Text(status_str, style=style)

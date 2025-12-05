from datetime import datetime
from typing import Any, List


def format_datetime(value: datetime) -> str:
    return value.isoformat()


def format_na(value: Any) -> str:
    return str(value) if value else "N/A"


def format_float(value: float | int, precision: int = 2) -> str:
    return f"{float(value):.{precision}f}"


def format_list(value: List[Any]) -> str:
    return ", ".join(value)

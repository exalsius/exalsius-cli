from __future__ import annotations

from typing import Protocol, TypeVar

T_Return_Cov = TypeVar("T_Return_Cov", covariant=True)


class BaseCommand(Protocol[T_Return_Cov]):
    """Base command with generic return type."""

    def execute(self) -> T_Return_Cov: ...

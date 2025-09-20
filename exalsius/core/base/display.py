from typing import List, Protocol, TypeVar

from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)

S = TypeVar("S")
T = TypeVar("T", contravariant=True)
U = TypeVar("U")


class BaseListDisplay(Protocol[S, U]):
    """Base display manager."""

    renderer: BaseListRenderer[S, U]

    def display(self, data: List[S]) -> None: ...


class BaseSingleItemDisplay(Protocol[T, U]):
    """Base display manager."""

    renderer: BaseSingleItemRenderer[T, U]

    def display(self, data: T) -> None: ...

from typing import List, Protocol, TypeVar

S = TypeVar("S")
T = TypeVar("T", contravariant=True)
U = TypeVar("U", covariant=True)


class BaseListRenderer(Protocol[S, U]):
    """Base list renderer."""

    def render(self, data: List[S]) -> U: ...


class BaseSingleItemRenderer(Protocol[T, U]):
    """Base single item renderer."""

    def render(self, data: T) -> U: ...

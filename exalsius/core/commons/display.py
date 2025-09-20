from typing import Generic, List, Optional

from rich.console import Console

from exalsius.core.base.display import BaseListDisplay, BaseSingleItemDisplay, T
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)
from exalsius.utils.theme import custom_theme


class ConsoleListDisplay(BaseListDisplay, Generic[T]):
    """Display manager for lists of items."""

    def __init__(
        self,
        renderer: BaseListRenderer[T, str],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self.renderer: BaseListRenderer[T, str] = renderer

    def display(self, data: List[T]) -> None:
        """Create a ListRenderableDTO and pass it to the renderer."""
        rendered_data: str = self.renderer.render(data)
        self.console.print(rendered_data)


class ConsoleSingleItemDisplay(BaseSingleItemDisplay, Generic[T]):
    """Display manager for single items."""

    def __init__(
        self,
        renderer: BaseSingleItemRenderer[T, str],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self.renderer: BaseSingleItemRenderer[T, str] = renderer

    def display(self, data: T) -> None:
        """Create a SingleItemRenderableDTO and pass it to the renderer."""
        rendered_data: str = self.renderer.render(data)
        self.console.print(rendered_data)

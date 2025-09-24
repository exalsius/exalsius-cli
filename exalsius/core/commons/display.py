from typing import Generic, List, Optional

from rich.console import Console
from rich.prompt import Confirm

from exalsius.core.base.display import (
    BaseConfirmationDisplay,
    BaseListDisplay,
    BaseSingleItemDisplay,
)
from exalsius.core.base.models import ErrorDTO
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
    T_RenderInput_Contra,
    T_RenderInput_Inv,
)
from exalsius.core.commons.render.json import (
    JsonMessageRenderer,
    JsonSingleItemStringRenderer,
)
from exalsius.core.commons.render.text import (
    RichTextErrorMessageRenderer,
    RichTextRenderer,
    RichTextSuccessMessageRenderer,
)
from exalsius.utils.theme import custom_theme


class ConsoleListDisplay(BaseListDisplay[T_RenderInput_Inv, str]):
    """Display manager for lists of items."""

    def __init__(
        self,
        renderer: BaseListRenderer[T_RenderInput_Inv, str],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseListRenderer[T_RenderInput_Inv, str] = renderer

    @property
    def renderer(self) -> BaseListRenderer[T_RenderInput_Inv, str]:
        return self._renderer

    def display(self, data: List[T_RenderInput_Inv]) -> None:
        """Create a ListRenderableDTO and pass it to the renderer."""
        rendered_data: str = self.renderer.render(data)
        self.console.print(rendered_data)


class ConsoleSingleItemDisplay(
    BaseSingleItemDisplay[T_RenderInput_Contra, str], Generic[T_RenderInput_Contra]
):
    """Display manager for single items."""

    def __init__(
        self,
        renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str] = renderer

    @property
    def renderer(self) -> BaseSingleItemRenderer[T_RenderInput_Contra, str]:
        return self._renderer

    def display(self, data: T_RenderInput_Contra) -> None:
        """Create a SingleItemRenderableDTO and pass it to the renderer."""
        rendered_data: str = self.renderer.render(data)
        self.console.print(rendered_data)


class ConsoleConfirmationDisplay(BaseConfirmationDisplay[T_RenderInput_Contra, str]):
    """Display manager for confirmation items."""

    def __init__(
        self,
        renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str] = renderer

    @property
    def renderer(self) -> BaseSingleItemRenderer[T_RenderInput_Contra, str]:
        return self._renderer

    def display(self, data: T_RenderInput_Contra) -> bool:
        """Create a SingleItemRenderableDTO and pass it to the renderer."""
        rendered_text: str = self.renderer.render(data)
        return Confirm.ask(rendered_text, console=self.console)


class BaseDisplayManager:
    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str],
        success_renderer: BaseSingleItemRenderer[str, str],
        error_renderer: BaseSingleItemRenderer[ErrorDTO, str],
        confirmation_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
    ):
        self.info_display = ConsoleSingleItemDisplay[str](renderer=info_renderer)
        self.success_display = ConsoleSingleItemDisplay[str](renderer=success_renderer)
        self.error_display = ConsoleSingleItemDisplay[ErrorDTO](renderer=error_renderer)
        self.confirmation_display = ConsoleConfirmationDisplay[str](
            renderer=confirmation_renderer
        )

    def display_info(self, message: str):
        self.info_display.display(message)

    def display_success(self, message: str):
        self.success_display.display(message)

    def display_error(self, error: ErrorDTO):
        self.error_display.display(error)

    def display_confirmation(self, message: str):
        return self.confirmation_display.display(message)


class BaseJsonDisplayManager(BaseDisplayManager):
    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str] = JsonMessageRenderer(
            message_key="message"
        ),
        success_renderer: BaseSingleItemRenderer[str, str] = JsonMessageRenderer(
            message_key="message"
        ),
        error_renderer: BaseSingleItemRenderer[
            ErrorDTO, str
        ] = JsonSingleItemStringRenderer[ErrorDTO](),
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
        )


class BaseTableDisplayManager(BaseDisplayManager):
    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
        success_renderer: BaseSingleItemRenderer[
            str, str
        ] = RichTextSuccessMessageRenderer(),
        error_renderer: BaseSingleItemRenderer[
            ErrorDTO, str
        ] = RichTextErrorMessageRenderer(),
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
        )

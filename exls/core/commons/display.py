from contextlib import AbstractContextManager
from typing import List, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.status import Status

from exls.core.base.display import (
    BaseConfirmationDisplay,
    BaseListDisplay,
    BaseSingleItemDisplay,
    BaseSpinnerDisplay,
    ErrorDisplayModel,
)
from exls.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
    T_RenderInput_Contra,
    T_RenderInput_Inv,
    T_RenderOutput_Cov,
)
from exls.core.commons.render.json import (
    JsonMessageRenderer,
    JsonSingleItemStringRenderer,
)
from exls.core.commons.render.text import (
    RichTextErrorMessageRenderer,
    RichTextRenderer,
    RichTextSuccessMessageRenderer,
    TextRenderConfig,
)
from exls.utils.theme import custom_theme


class ConsoleListDisplay(BaseListDisplay[T_RenderInput_Inv, T_RenderOutput_Cov]):
    """Display manager for lists of items."""

    def __init__(
        self,
        renderer: BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov] = (
            renderer
        )

    @property
    def renderer(self) -> BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov]:
        return self._renderer

    def display(self, data: List[T_RenderInput_Inv]) -> None:
        """Create a ListRenderableDTO and pass it to the renderer."""
        rendered_data: T_RenderOutput_Cov = self.renderer.render(data)
        self.console.print(rendered_data)


class ConsoleSingleItemDisplay(
    BaseSingleItemDisplay[T_RenderInput_Contra, T_RenderOutput_Cov],
):
    """Display manager for single items."""

    def __init__(
        self,
        renderer: BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov],
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseSingleItemRenderer[
            T_RenderInput_Contra, T_RenderOutput_Cov
        ] = renderer

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]:
        return self._renderer

    def display(self, data: T_RenderInput_Contra) -> None:
        """Create a SingleItemRenderableDTO and pass it to the renderer."""
        rendered_data: T_RenderOutput_Cov = self.renderer.render(data)
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


class ConsoleSpinnerDisplay(BaseSpinnerDisplay[T_RenderInput_Contra, str]):
    """Display manager for spinner items."""

    def __init__(
        self,
        renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str],
        console: Optional[Console] = None,
        spinner: str = "bouncingBall",
        spinner_style: str = "custom",
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self._renderer: BaseSingleItemRenderer[T_RenderInput_Contra, str] = renderer
        self._status: Optional[AbstractContextManager[Status]] = None
        self._spinner: str = spinner
        self._spinner_style: str = spinner_style

    @property
    def renderer(self) -> BaseSingleItemRenderer[T_RenderInput_Contra, str]:
        return self._renderer

    def start_display(self, data: T_RenderInput_Contra) -> None:
        self._status = self.console.status(
            self._renderer.render(data),
            spinner=self._spinner,
            spinner_style=self._spinner_style,
        )

    def stop_display(self) -> None:
        if self._status:
            self._status.__exit__(None, None, None)
            self._status = None


class BaseDisplayManager:
    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str],
        success_renderer: BaseSingleItemRenderer[str, str],
        error_renderer: BaseSingleItemRenderer[ErrorDisplayModel, str],
        confirmation_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
        spinner_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(
            render_config=TextRenderConfig(bold=True, color="custom")
        ),
    ):
        self.info_display: BaseSingleItemDisplay[str, str] = ConsoleSingleItemDisplay(
            renderer=info_renderer,
        )
        self.success_display: BaseSingleItemDisplay[str, str] = (
            ConsoleSingleItemDisplay(
                renderer=success_renderer,
            )
        )
        self.error_display: BaseSingleItemDisplay[ErrorDisplayModel, str] = (
            ConsoleSingleItemDisplay(
                renderer=error_renderer,
            )
        )
        self.confirmation_display: BaseConfirmationDisplay[str, str] = (
            ConsoleConfirmationDisplay(
                renderer=confirmation_renderer,
            )
        )
        self.spinner_display: BaseSpinnerDisplay[str, str] = ConsoleSpinnerDisplay(
            renderer=spinner_renderer
        )

    def display_info(self, message: str):
        self.info_display.display(message)

    def display_success(self, message: str):
        self.success_display.display(message)

    def display_error(self, error: ErrorDisplayModel):
        self.error_display.display(error)

    def display_confirmation(self, message: str) -> bool:
        return self.confirmation_display.display(message)

    def start_spinner_display(self, message: str):
        self.spinner_display.start_display(message)

    def stop_spinner_display(self):
        self.spinner_display.stop_display()


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
            ErrorDisplayModel, str
        ] = JsonSingleItemStringRenderer[ErrorDisplayModel](),
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
            ErrorDisplayModel, str
        ] = RichTextErrorMessageRenderer(),
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
        )

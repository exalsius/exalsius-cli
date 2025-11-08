import re
from contextlib import AbstractContextManager
from typing import Callable, List, Optional, Protocol

import questionary
from pydantic import StrictStr
from rich.console import Console
from rich.prompt import Confirm
from rich.status import Status
from rich.theme import Theme

from exls.core.base.display import (
    BaseConfirmationDisplay,
    BaseListDisplay,
    BaseSingleItemDisplay,
    BaseSpinnerDisplay,
    ErrorDisplayModel,
    InteractiveDisplay,
    UserCancellationException,
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

DEFAULT_THEME = Theme(
    {
        "custom": "#f46907",
    }
)


class ConsoleListDisplay(BaseListDisplay[T_RenderInput_Inv, T_RenderOutput_Cov]):
    """Display manager for lists of items."""

    def __init__(
        self,
        renderer: BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov],
        theme: Theme = DEFAULT_THEME,
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=theme)
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
        theme: Theme = DEFAULT_THEME,
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=theme)
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
        theme: Theme = DEFAULT_THEME,
        console: Optional[Console] = None,
    ):
        self.console: Console = console or Console(theme=theme)
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
        theme: Theme = DEFAULT_THEME,
        console: Optional[Console] = None,
        spinner: str = "bouncingBall",
        spinner_style: str = "custom",
    ):
        self.console: Console = console or Console(theme=theme)
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


class BaseDisplayManager(Protocol):
    """Base display manager protocol."""

    def display_info(self, message: str): ...
    def display_success(self, message: str): ...
    def display_error(self, error: ErrorDisplayModel): ...
    def display_confirmation(self, message: str) -> bool: ...
    def start_spinner_display(self, message: str): ...
    def stop_spinner_display(self): ...


class SimpleDisplayManager(BaseDisplayManager):
    """Simple display manager that uses renderers to display messages."""

    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str],
        success_renderer: BaseSingleItemRenderer[str, str],
        error_renderer: BaseSingleItemRenderer[ErrorDisplayModel, str],
        confirmation_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
        spinner_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(
            render_config=TextRenderConfig(bold=True, color="custom")
        ),
        theme: Theme = DEFAULT_THEME,
    ):
        self.info_display: BaseSingleItemDisplay[str, str] = ConsoleSingleItemDisplay(
            renderer=info_renderer, theme=theme
        )
        self.success_display: BaseSingleItemDisplay[str, str] = (
            ConsoleSingleItemDisplay(renderer=success_renderer, theme=theme)
        )
        self.error_display: BaseSingleItemDisplay[ErrorDisplayModel, str] = (
            ConsoleSingleItemDisplay(renderer=error_renderer, theme=theme)
        )
        self.confirmation_display: BaseConfirmationDisplay[str, str] = (
            ConsoleConfirmationDisplay(renderer=confirmation_renderer, theme=theme)
        )
        self.spinner_display: BaseSpinnerDisplay[str, str] = ConsoleSpinnerDisplay(
            renderer=spinner_renderer, theme=theme
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


class BaseJsonDisplayManager(SimpleDisplayManager):
    """Base JSON display manager that uses renderers to display messages."""

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
        theme: Theme = DEFAULT_THEME,
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
            theme=theme,
        )


class BaseTableDisplayManager(SimpleDisplayManager):
    """Base table display manager that uses renderers to display messages."""

    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
        success_renderer: BaseSingleItemRenderer[
            str, str
        ] = RichTextSuccessMessageRenderer(),
        error_renderer: BaseSingleItemRenderer[
            ErrorDisplayModel, str
        ] = RichTextErrorMessageRenderer(),
        theme: Theme = DEFAULT_THEME,
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
            theme=theme,
        )


class SimpleTextDisplayManager(SimpleDisplayManager):
    """Base text display manager that uses renderers to display messages."""

    def __init__(
        self,
        info_renderer: BaseSingleItemRenderer[str, str] = RichTextRenderer(),
        success_renderer: BaseSingleItemRenderer[
            str, str
        ] = RichTextSuccessMessageRenderer(),
        error_renderer: BaseSingleItemRenderer[
            ErrorDisplayModel, str
        ] = RichTextErrorMessageRenderer(),
        theme: Theme = DEFAULT_THEME,
    ):
        super().__init__(
            info_renderer=info_renderer,
            success_renderer=success_renderer,
            error_renderer=error_renderer,
            theme=theme,
        )


class QuestionaryInteractionHandler(InteractiveDisplay[questionary.Choice]):
    """Handler for interactive prompts using the questionary library."""

    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> StrictStr:
        """Ask a free-form text question."""

        result = questionary.text(
            message,
            default=default or "",
            validate=validator,
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_select_required(
        self,
        message: str,
        choices: List[questionary.Choice],
        default: questionary.Choice,
    ) -> questionary.Choice:
        """Ask the user to select one option from a list."""
        result = questionary.select(message, choices=choices, default=default).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_select_optional(
        self,
        message: str,
        choices: List[questionary.Choice],
        default: Optional[questionary.Choice] = None,
    ) -> Optional[questionary.Choice]:
        result = questionary.select(message, choices=choices, default=default).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_confirm(self, message: str, default: bool = False) -> bool:
        """Ask a yes/no confirmation question."""
        result = questionary.confirm(message, default=default).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_checkbox(
        self, message: str, choices: List[questionary.Choice], min_choices: int = 1
    ) -> List[questionary.Choice]:
        """Ask the user to select multiple options from a list."""

        def _validate_checkbox(choices: List[str]) -> bool | str:
            return (
                True
                if len(choices) >= min_choices
                else "Please select at least {min_choices} options."
            )

        result = questionary.checkbox(
            message, choices=choices, validate=_validate_checkbox
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result


def non_empty_string_validator(text: str) -> bool | str:
    """Validator for non-empty strings."""
    return True if len(text.strip()) > 0 else "Please enter a valid string."


def kubernetes_name_validator(text: str) -> bool | str:
    """Validator for Kubernetes names."""
    if len(text) > 63:
        return "Name must be 63 characters or less."
    if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", text):
        return "Name must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character."
    return True


def ipv4_address_validator(text: str) -> bool | str:
    """Validator for IPv4 addresses."""
    if not re.match(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        text,
    ):
        return "Please enter a valid IPv4 address."
    return True


def positive_integer_validator(text: str) -> bool | str:
    """Validator for positive integers."""
    try:
        int(text)
    except ValueError:
        return "Please enter a valid integer."
    return True if int(text) > 0 else "Please enter a positive integer."


class ComposingDisplayManager(
    BaseDisplayManager, InteractiveDisplay[questionary.Choice]
):
    """A display manager that composes text display with an interactive handler."""

    def __init__(
        self,
        display_manager: BaseDisplayManager,
        interaction_handler: InteractiveDisplay[
            questionary.Choice
        ] = QuestionaryInteractionHandler(),
    ):
        self._interaction_handler: InteractiveDisplay[questionary.Choice] = (
            interaction_handler
        )
        self._display_manager: BaseDisplayManager = display_manager

    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> StrictStr:
        return self._interaction_handler.ask_text(message, default, validator)

    def ask_select_required(
        self,
        message: str,
        choices: List[questionary.Choice],
        default: questionary.Choice,
    ) -> questionary.Choice:
        return self._interaction_handler.ask_select_required(message, choices, default)

    def ask_select_optional(
        self,
        message: str,
        choices: List[questionary.Choice],
        default: Optional[questionary.Choice] = None,
    ) -> Optional[questionary.Choice]:
        return self._interaction_handler.ask_select_optional(message, choices, default)

    def ask_confirm(self, message: str, default: bool = False) -> bool:
        return self._interaction_handler.ask_confirm(message, default)

    def ask_checkbox(
        self, message: str, choices: List[questionary.Choice], min_choices: int = 1
    ) -> List[questionary.Choice]:
        return self._interaction_handler.ask_checkbox(message, choices, min_choices)

    def display_info(self, message: str):
        self._display_manager.display_info(message)

    def display_success(self, message: str):
        self._display_manager.display_success(message)

    def display_error(self, error: ErrorDisplayModel):
        self._display_manager.display_error(error)

    def display_confirmation(self, message: str) -> bool:
        return self._display_manager.display_confirmation(message)

    def start_spinner_display(self, message: str):
        self._display_manager.start_spinner_display(message)

    def stop_spinner_display(self):
        self._display_manager.stop_spinner_display()

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

import questionary
from pydantic import BaseModel, StrictStr
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from exls.shared.adapters.ui.display.interfaces import (
    IBaseInputManager,
    IListRenderer,
    IMessageOutputManager,
    IOutputManager,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.display.render.entities import (
    BaseRenderContext,
    TextMessageItem,
)
from exls.shared.adapters.ui.display.render.factory import (
    DefaultRendererProvider,
    RendererProvider,
)
from exls.shared.adapters.ui.display.render.json import JsonRenderContext
from exls.shared.adapters.ui.display.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.display.render.text import TextRenderContext
from exls.shared.adapters.ui.display.render.yaml import YamlRenderContext
from exls.shared.adapters.ui.display.values import (
    DisplayChoice,
    OutputFormat,
)
from exls.shared.core.domain import ExalsiusWarning

DEFAULT_THEME = Theme(
    {
        "custom": "#f46907",
    }
)


class UserCancellationException(ExalsiusWarning):
    """Raised when the user cancels an interactive operation."""


class IBaseModelDisplayOutputManager(IMessageOutputManager, ABC):
    """Protocol for displaying data of a shared base model."""

    @abstractmethod
    def display_data(
        self, data: Union[BaseModel, Sequence[BaseModel]], output_format: OutputFormat
    ): ...


class BaseModelInteractionManager(IBaseModelDisplayOutputManager):
    def __init__(
        self,
        input_manager: IBaseInputManager,
        output_manager: IOutputManager[BaseModel, Union[Table, str]],
    ):
        self.input_manager: IBaseInputManager = input_manager
        self.output_manager: IOutputManager[BaseModel, Union[Table, str]] = (
            output_manager
        )

    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        # Subclasses can override this method to e.g. return the columns rendering map
        return None

    def _display_sequence(
        self,
        data: Sequence[BaseModel],
        output_format: OutputFormat,
        render_context: Optional[TableRenderContext] = None,
    ):
        if output_format == OutputFormat.TABLE:
            self.output_manager.display(
                data, output_format=output_format, render_context=render_context
            )
        else:
            self.output_manager.display(
                data, output_format=output_format, render_context=None
            )

    def display_data(
        self,
        data: Union[BaseModel, Sequence[BaseModel]],
        output_format: OutputFormat,
    ):
        if isinstance(data, Sequence):
            if not data:
                self.output_manager.display(
                    [], output_format=output_format, render_context=None
                )
                return

            columns: Optional[Dict[str, Column]] = self.get_columns_rendering_map(
                type(data[0])
            )
            render_context: Optional[TableRenderContext] = None
            if columns and output_format == OutputFormat.TABLE:
                render_context = TableRenderContext.get_table_render_context(
                    columns=columns
                )
            self._display_sequence(
                data, output_format=output_format, render_context=render_context
            )
        else:
            self.output_manager.display(
                data,
                output_format=output_format,
                render_context=None,
            )

    def display_info_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_info_message(message, output_format)

    def display_success_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_success_message(message, output_format)

    def display_error_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_error_message(message, output_format)

    def ask_for_confirmation(self, message: str) -> bool:
        return self.input_manager.ask_confirm(message=message, default=False)


class QuestionaryInputManager(IBaseInputManager):
    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> StrictStr:
        """Ask a free-form text question."""

        result: Optional[StrictStr] = questionary.text(
            message,
            default=default or "",
            validate=validator,
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def _to_questionary_choice(self, choice: DisplayChoice) -> questionary.Choice:
        if isinstance(choice, str):
            return questionary.Choice(title=choice, value=choice)
        return questionary.Choice(
            title=choice.title,
            value=choice.value,
            disabled=choice.disabled,
            checked=choice.checked,
        )

    def _resolve_default(
        self,
        default: Optional[DisplayChoice],
        choices: Sequence[DisplayChoice],
        mapped_choices: List[questionary.Choice],
    ) -> Optional[questionary.Choice]:
        if default is None:
            return None

        # If default is one of the choices objects (reference equality), find it in mapped
        if default in choices:
            index = choices.index(default)
            return mapped_choices[index]

        # Fallback: try to match by value or title
        for mc in mapped_choices:
            if mc.value == default.value or mc.title == default.title:
                return mc
        return None

    def ask_select_required(
        self,
        message: str,
        choices: Sequence[DisplayChoice],
        default: DisplayChoice,
    ) -> Any:
        """Ask the user to select one option from a list."""
        q_choices = [self._to_questionary_choice(c) for c in choices]
        q_default = self._resolve_default(default, choices, q_choices)

        result: Any = questionary.select(
            message, choices=q_choices, default=q_default
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_select_optional(
        self,
        message: str,
        choices: Sequence[DisplayChoice],
        default: Optional[DisplayChoice] = None,
    ) -> Optional[Any]:
        q_choices = [self._to_questionary_choice(c) for c in choices]
        q_default = self._resolve_default(default, choices, q_choices)

        # We need to ask_unsafe to detect KeyboardInterrupt and allow None-selection
        try:
            result: Any = questionary.select(
                message, choices=q_choices, default=q_default
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise UserCancellationException("User cancelled")
        return result

    def ask_confirm(self, message: str, default: bool = False) -> bool:
        """Ask a yes/no confirmation question."""
        result = questionary.confirm(message, default=default).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_checkbox(
        self, message: str, choices: Sequence[DisplayChoice], min_choices: int = 1
    ) -> List[Any]:
        """Ask the user to select multiple options from a list."""

        def _validate_checkbox(choices: List[Any]) -> bool | str:
            return (
                True
                if len(choices) >= min_choices
                else f"Please select at least {min_choices} options."
            )

        q_choices = [self._to_questionary_choice(c) for c in choices]

        result: Optional[List[Any]] = questionary.checkbox(
            message, choices=q_choices, validate=_validate_checkbox
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result or []


T_Output_Cov = TypeVar("T_Output_Cov", bound=Union[Table, str])


class TyperConsoleOutputManager(
    IOutputManager[BaseModel, T_Output_Cov],
    IMessageOutputManager,
    Generic[T_Output_Cov],
):
    def __init__(
        self,
        object_renderer_provider: Optional[RendererProvider[BaseModel]] = None,
    ):
        self.console = Console(theme=DEFAULT_THEME)
        self.renderer_provider: RendererProvider[BaseModel] = (
            object_renderer_provider or DefaultRendererProvider[BaseModel]()
        )

    def _get_list_renderer(
        self,
        output_format: OutputFormat,
    ) -> IListRenderer[BaseModel, Union[Table, str]]:
        return self.renderer_provider.get_list_renderer(output_format)

    def _get_item_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[BaseModel, Union[Table, str]]:
        return self.renderer_provider.get_item_renderer(output_format)

    def _get_info_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.renderer_provider.get_message_renderer(output_format)

    def _get_success_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.renderer_provider.get_success_message_renderer(output_format)

    def _get_error_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.renderer_provider.get_error_renderer(output_format)

    @overload
    def display(
        self,
        data: Sequence[BaseModel] | BaseModel,
        output_format: Literal[OutputFormat.TABLE],
        render_context: Optional[TableRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[BaseModel] | BaseModel,
        output_format: Literal[OutputFormat.JSON],
        render_context: Optional[JsonRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[BaseModel] | BaseModel,
        output_format: Literal[OutputFormat.YAML],
        render_context: Optional[YamlRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[BaseModel] | BaseModel,
        output_format: Literal[OutputFormat.TEXT],
        render_context: Optional[TextRenderContext] = None,
    ) -> None: ...

    def display(
        self,
        data: Sequence[BaseModel] | BaseModel,
        output_format: OutputFormat,
        render_context: Optional[BaseRenderContext] = None,
    ) -> None:
        if isinstance(data, BaseModel):
            single_item_renderer: ISingleItemRenderer[BaseModel, Union[Table, str]] = (
                self._get_item_renderer(output_format)
            )
            self.console.print(single_item_renderer.render(data, render_context))
        else:
            list_renderer: IListRenderer[BaseModel, Union[Table, str]] = (
                self._get_list_renderer(output_format)
            )
            self.console.print(list_renderer.render(data, render_context))

    def display_info_message(self, message: str, output_format: OutputFormat):
        item = TextMessageItem(message=message)
        renderer: ISingleItemRenderer[TextMessageItem, Union[Table, str]] = (
            self._get_info_message_renderer(output_format)
        )
        self.console.print(renderer.render(item))

    def display_success_message(self, message: str, output_format: OutputFormat):
        item = TextMessageItem(message=message)
        renderer: ISingleItemRenderer[TextMessageItem, Union[Table, str]] = (
            self._get_success_message_renderer(output_format)
        )
        self.console.print(renderer.render(item))

    def display_error_message(self, message: str, output_format: OutputFormat):
        item = TextMessageItem(message=message)
        renderer: ISingleItemRenderer[TextMessageItem, Union[Table, str]] = (
            self._get_error_message_renderer(output_format)
        )
        self.console.print(renderer.render(item))

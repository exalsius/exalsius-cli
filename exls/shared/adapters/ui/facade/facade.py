from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from rich.table import Table

from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.adapters.ui.output.interfaces import (
    IOutputManager,
)
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.output.view import ViewContext
from exls.shared.adapters.ui.shared.render.render import (
    DictToYamlStringRenderer,
    YamlRenderContext,
)

T = TypeVar("T")


class IOBaseModelFacade(IOFacade[BaseModel]):
    def __init__(
        self,
        output_manager: IOutputManager[BaseModel, Union[Table, str]],
        input_manager: IInputManager,
    ):
        self.input_manager: IInputManager = input_manager
        self.output_manager: IOutputManager[BaseModel, Union[Table, str]] = (
            output_manager
        )

    def display_data(
        self,
        data: Union[BaseModel, Sequence[BaseModel]],
        output_format: OutputFormat,
        view_context: Optional[ViewContext] = None,
    ):
        # We need to ignore the type errors because the output manager is generic is not
        # able to infer the type of the render context, although we know it is valid.
        self.output_manager.display(  # type: ignore
            data,
            output_format=output_format,  # type: ignore
            render_context=(
                view_context.get_context_for_format(output_format)
                if view_context
                else None
            ),  # type: ignore
        )

    def display_stream(
        self,
        stream: Iterator[BaseModel],
        output_format: OutputFormat,
        view_context: Optional[ViewContext] = None,
        header: Optional[str] = None,
    ):
        self.output_manager.display_stream(
            stream,
            output_format=output_format,  # type: ignore
            render_context=(
                view_context.get_context_for_format(output_format)
                if view_context
                else None
            ),  # type: ignore
            header=header,
        )

    def display_info_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_info_message(message, output_format)

    def display_success_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_success_message(message, output_format)

    def display_error_message(self, message: str, output_format: OutputFormat):
        self.output_manager.display_error_message(message, output_format)

    def ask_confirm(self, message: str, default: bool = False) -> bool:
        return self.input_manager.ask_confirm(message=message, default=False)

    def ask_path(
        self,
        message: str,
        default: Optional[Path] = None,
    ) -> Path:
        return self.input_manager.ask_path(message=message, default=default)

    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> str:
        return self.input_manager.ask_text(
            message=message, default=default, validator=validator
        )

    def ask_password(
        self,
        message: str,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> str:
        return self.input_manager.ask_password(message=message, validator=validator)

    def ask_select_required(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: DisplayChoice[T],
    ) -> DisplayChoice[T]:
        return self.input_manager.ask_select_required(
            message=message, choices=choices, default=default
        )

    def ask_select_optional(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ) -> Optional[DisplayChoice[T]]:
        return self.input_manager.ask_select_optional(
            message=message, choices=choices, default=default
        )

    def ask_checkbox(
        self, message: str, choices: Sequence[DisplayChoice[T]], min_choices: int = 1
    ) -> Sequence[DisplayChoice[T]]:
        return self.input_manager.ask_checkbox(
            message=message, choices=choices, min_choices=min_choices
        )

    def edit_dictionary(
        self,
        dictionary: Dict[str, Any],
        renderer: DictToYamlStringRenderer,
        render_context: Optional[YamlRenderContext] = None,
    ) -> Dict[str, Any]:
        return self.input_manager.edit_dictionary(
            dictionary=dictionary, renderer=renderer
        )

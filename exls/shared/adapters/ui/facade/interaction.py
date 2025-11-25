from pathlib import Path
from typing import (
    Callable,
    Dict,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from rich.table import Table

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.adapters.ui.output.interfaces import (
    IOutputManager,
)
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.values import OutputFormat

T = TypeVar("T")


class IOBaseModelFacade(IIOFacade[BaseModel]):
    def __init__(
        self,
        output_manager: IOutputManager[BaseModel, Union[Table, str]],
        input_manager: IInputManager,
    ):
        self.input_manager: IInputManager = input_manager
        self.output_manager: IOutputManager[BaseModel, Union[Table, str]] = (
            output_manager
        )

    def get_columns_rendering_map(
        self, data_type: Type[BaseModel]
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

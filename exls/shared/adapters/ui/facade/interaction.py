from pathlib import Path
from typing import (
    Any,
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
from exls.shared.adapters.ui.shared.render.render import (
    DictToYamlStringRenderer,
    YamlRenderContext,
)

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

    def _get_render_context(
        self, data: BaseModel, output_format: OutputFormat
    ) -> Optional[TableRenderContext]:
        columns: Optional[Dict[str, Column]] = self.get_columns_rendering_map(
            type(data)
        )
        render_context: Optional[TableRenderContext] = None
        if columns and output_format == OutputFormat.TABLE:
            render_context = TableRenderContext.get_table_render_context(
                columns=columns
            )
        return render_context

    def display_data(
        self,
        data: Union[BaseModel, Sequence[BaseModel]],
        output_format: OutputFormat,
    ):
        render_context: Optional[TableRenderContext] = None
        if output_format == OutputFormat.TABLE:
            ref_data: Optional[BaseModel] = (
                data[0]
                if isinstance(data, Sequence) and len(data) > 0
                else data if isinstance(data, BaseModel) else None
            )
            if ref_data:
                render_context = self._get_render_context(ref_data, output_format)
            self.output_manager.display(
                data, output_format=output_format, render_context=render_context
            )
        else:
            self.output_manager.display(
                data, output_format=output_format, render_context=None
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

from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel

from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.output.interfaces import IMessageOutputManager
from exls.shared.adapters.ui.output.render.table import Column
from exls.shared.adapters.ui.output.values import OutputFormat

T = TypeVar("T", bound=BaseModel)


class IIOFacade(
    IMessageOutputManager,
    IInputManager,
    Generic[T],
    ABC,
):
    @abstractmethod
    def get_columns_rendering_map(
        self, data_type: Type[T], list_data: bool = False
    ) -> Optional[Dict[str, Column]]: ...

    @abstractmethod
    def display_data(
        self,
        data: Union[T, Sequence[T]],
        output_format: OutputFormat,
    ) -> None: ...

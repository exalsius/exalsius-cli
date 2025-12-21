from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel

from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.output.interfaces import IMessageOutputManager
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.output.view import ViewContext

T = TypeVar("T", bound=BaseModel)


class IOFacade(
    IMessageOutputManager,
    IInputManager,
    Generic[T],
    ABC,
):
    @abstractmethod
    def display_data(
        self,
        data: Union[T, Sequence[T]],
        output_format: OutputFormat,
        view_context: Optional[ViewContext] = None,
    ) -> None: ...

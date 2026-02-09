from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Generic,
    Iterator,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    overload,
)

from exls.shared.adapters.ui.shared.render.render import YamlRenderContext

if TYPE_CHECKING:
    from exls.shared.adapters.ui.output.render.json import JsonRenderContext
    from exls.shared.adapters.ui.output.render.table import TableRenderContext
    from exls.shared.adapters.ui.output.render.text import TextRenderContext
    from exls.shared.adapters.ui.output.values import OutputFormat
    from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext

T_Input_Cov = TypeVar("T_Input_Cov", contravariant=True)
T_Output_Cov = TypeVar("T_Output_Cov", covariant=True)


class IListRenderer(Generic[T_Input_Cov, T_Output_Cov], ABC):
    """Base list renderer."""

    @abstractmethod
    def render(
        self,
        data: Sequence[T_Input_Cov],
        render_context: Optional[BaseRenderContext] = None,
    ) -> T_Output_Cov: ...


class ISingleItemRenderer(Generic[T_Input_Cov, T_Output_Cov], ABC):
    """Base single item renderer."""

    @abstractmethod
    def render(
        self, data: T_Input_Cov, render_context: Optional[BaseRenderContext] = None
    ) -> T_Output_Cov: ...


class IObjectOutputManager(
    Generic[T_Input_Cov, T_Output_Cov],
    ABC,
):
    """Protocol for output display operations."""

    @overload
    def display(
        self,
        data: Sequence[T_Input_Cov] | T_Input_Cov,
        output_format: Literal[OutputFormat.TABLE],
        render_context: Optional[TableRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T_Input_Cov] | T_Input_Cov,
        output_format: Literal[OutputFormat.JSON],
        render_context: Optional[JsonRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T_Input_Cov] | T_Input_Cov,
        output_format: Literal[OutputFormat.YAML],
        render_context: Optional[YamlRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T_Input_Cov] | T_Input_Cov,
        output_format: Literal[OutputFormat.TEXT],
        render_context: Optional[TextRenderContext] = None,
    ) -> None: ...

    @abstractmethod
    def display(
        self,
        data: Sequence[T_Input_Cov] | T_Input_Cov,
        output_format: OutputFormat,
        render_context: Optional[BaseRenderContext] = None,
    ) -> None: ...

    @abstractmethod
    def display_stream(
        self,
        stream: Iterator[T_Input_Cov],
        output_format: OutputFormat,
        render_context: Optional[BaseRenderContext] = None,
        header: Optional[str] = None,
    ) -> None: ...


class IMessageOutputManager(ABC):
    """Protocol for output display of messages."""

    @abstractmethod
    def display_info_message(
        self, message: str, output_format: OutputFormat
    ) -> None: ...

    @abstractmethod
    def display_success_message(
        self, message: str, output_format: OutputFormat
    ) -> None: ...

    @abstractmethod
    def display_error_message(
        self, message: str, output_format: OutputFormat
    ) -> None: ...


class IOutputManager(
    IMessageOutputManager,
    IObjectOutputManager[T_Input_Cov, T_Output_Cov],
    Generic[T_Input_Cov, T_Output_Cov],
    ABC,
):
    """Protocol for output display operations."""

from contextlib import contextmanager
from typing import (
    Generator,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    IMessageOutputManager,
    IOutputManager,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.output.render.entities import (
    TextMessageItem,
)
from exls.shared.adapters.ui.output.render.factory import (
    DefaultRendererProvider,
    RendererProvider,
)
from exls.shared.adapters.ui.output.render.json import JsonRenderContext
from exls.shared.adapters.ui.output.render.table import TableRenderContext
from exls.shared.adapters.ui.output.render.text import TextRenderContext
from exls.shared.adapters.ui.output.values import (
    OutputFormat,
)
from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext
from exls.shared.adapters.ui.shared.render.render import YamlRenderContext

DEFAULT_THEME = Theme(
    {
        "custom": "#f46907",
    }
)


T = TypeVar("T", bound=BaseModel)


class TyperConsoleOutputManager(
    IOutputManager[T, Union[Table, str]],
    IMessageOutputManager,
    Generic[T],
):
    def __init__(
        self,
        object_renderer_provider: Optional[RendererProvider[T]] = None,
        message_renderer_provider: Optional[RendererProvider[TextMessageItem]] = None,
    ):
        self.console = Console(theme=DEFAULT_THEME)
        self.object_renderer_provider: RendererProvider[T] = (
            object_renderer_provider or DefaultRendererProvider[T]()
        )
        self.message_renderer_provider: RendererProvider[TextMessageItem] = (
            message_renderer_provider or DefaultRendererProvider[TextMessageItem]()
        )

    def _get_list_renderer(
        self,
        output_format: OutputFormat,
    ) -> IListRenderer[T, Union[Table, str]]:
        return self.object_renderer_provider.get_list_renderer(output_format)

    def _get_item_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[T, Union[Table, str]]:
        return self.object_renderer_provider.get_item_renderer(output_format)

    def _get_info_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.message_renderer_provider.get_message_renderer(output_format)

    def _get_success_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.message_renderer_provider.get_success_message_renderer(
            output_format
        )

    def _get_error_message_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        return self.message_renderer_provider.get_error_renderer(output_format)

    @overload
    def display(
        self,
        data: Sequence[T] | T,
        output_format: Literal[OutputFormat.TABLE],
        render_context: Optional[TableRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T] | T,
        output_format: Literal[OutputFormat.JSON],
        render_context: Optional[JsonRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T] | T,
        output_format: Literal[OutputFormat.YAML],
        render_context: Optional[YamlRenderContext] = None,
    ) -> None: ...

    @overload
    def display(
        self,
        data: Sequence[T] | T,
        output_format: Literal[OutputFormat.TEXT],
        render_context: Optional[TextRenderContext] = None,
    ) -> None: ...

    def display(
        self,
        data: Sequence[T] | T,
        output_format: OutputFormat,
        render_context: Optional[BaseRenderContext] = None,
    ) -> None:
        if isinstance(data, Sequence):
            list_renderer: IListRenderer[T, Union[Table, str]] = (
                self._get_list_renderer(output_format)
            )
            self.console.print(list_renderer.render(data, render_context))
        else:
            single_item_renderer: ISingleItemRenderer[T, Union[Table, str]] = (
                self._get_item_renderer(output_format)
            )
            self.console.print(single_item_renderer.render(data, render_context))

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

    @contextmanager
    def spinner(self, message: str) -> Generator[None, None, None]:
        """Display a spinner with a message while a long-running operation is in progress."""
        with self.console.status(message, spinner="dots"):
            yield

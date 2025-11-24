from typing import Generic, Optional, Protocol, Sequence, TypeVar, Union

from pydantic import BaseModel
from rich.table import Table

from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.output.render.entities import (
    BaseRenderContext,
    TextMessageItem,
)
from exls.shared.adapters.ui.output.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exls.shared.adapters.ui.output.render.table import (
    TableListRenderer,
    TableSingleItemRenderer,
)
from exls.shared.adapters.ui.output.render.text import (
    RichTextErrorMessageRenderer,
    RichTextInfoMessageRenderer,
    RichTextItemRenderer,
    RichTextListRenderer,
    RichTextSuccessMessageRenderer,
)
from exls.shared.adapters.ui.output.render.yaml import (
    YamlListStringRenderer,
    YamlSingleItemStringRenderer,
)
from exls.shared.adapters.ui.output.values import (
    OutputFormat,
)

T = TypeVar("T", contravariant=True, bound=BaseModel)


class SimpleStringListRenderer(IListRenderer[T, str]):
    def render(
        self, data: Sequence[T], render_context: Optional[BaseRenderContext] = None
    ) -> str:
        return "\n".join(str(item) for item in data)


class SimpleStringItemRenderer(ISingleItemRenderer[T, str]):
    def render(
        self, data: T, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        return str(data)


class RendererProvider(Protocol, Generic[T]):
    """Protocol for providing renderers based on format."""

    def get_list_renderer(
        self,
        output_format: OutputFormat,
    ) -> IListRenderer[T, Union[Table, str]]: ...

    def get_item_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[T, Union[Table, str]]: ...

    def get_message_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]: ...

    def get_success_message_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]: ...

    def get_error_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]: ...


class DefaultRendererProvider(RendererProvider[T], Generic[T]):
    """Default implementation of RendererProvider."""

    def get_list_renderer(
        self,
        output_format: OutputFormat,
    ) -> IListRenderer[T, Union[Table, str]]:
        if output_format == OutputFormat.JSON:
            return JsonListStringRenderer[T]()
        elif output_format == OutputFormat.YAML:
            return YamlListStringRenderer[T]()
        elif output_format == OutputFormat.TABLE:
            return TableListRenderer[T]()
        elif output_format == OutputFormat.TEXT:
            return RichTextListRenderer[T]()

    def get_item_renderer(
        self,
        output_format: OutputFormat,
    ) -> ISingleItemRenderer[T, Union[Table, str]]:
        if output_format == OutputFormat.JSON:
            return JsonSingleItemStringRenderer[T]()
        elif output_format == OutputFormat.YAML:
            return YamlSingleItemStringRenderer[T]()
        elif output_format == OutputFormat.TABLE:
            return TableSingleItemRenderer[T]()
        elif output_format == OutputFormat.TEXT:
            return RichTextItemRenderer[T]()

    def get_message_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        if output_format == OutputFormat.TEXT:
            return RichTextInfoMessageRenderer()
        elif output_format == OutputFormat.JSON:
            return JsonSingleItemStringRenderer[TextMessageItem]()
        elif output_format == OutputFormat.YAML:
            return YamlSingleItemStringRenderer[TextMessageItem]()
        elif output_format == OutputFormat.TABLE:
            return TableSingleItemRenderer[TextMessageItem]()

    def get_success_message_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        if output_format == OutputFormat.TEXT:
            return RichTextSuccessMessageRenderer()
        else:
            return self.get_message_renderer(output_format)

    def get_error_renderer(
        self, output_format: OutputFormat
    ) -> ISingleItemRenderer[TextMessageItem, Union[Table, str]]:
        if output_format == OutputFormat.TEXT:
            return RichTextErrorMessageRenderer()
        else:
            return self.get_message_renderer(output_format)

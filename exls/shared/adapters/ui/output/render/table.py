from __future__ import annotations

import functools
import logging
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import JustifyMethod
from rich.style import Style, StyleType
from rich.table import Table

from exls.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext

T = TypeVar("T", bound=BaseModel)


def _get_nested_attribute(obj: Any, attr: str, default: Any = "") -> Any:
    """
    Safely retrieves a nested attribute from an object using dot notation.
    For example, for an attribute `a.b.c`, it will try to get `obj.a.b.c`.
    If any attribute in the chain does not exist, it returns the default value.
    """
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except (AttributeError, TypeError) as e:
        logging.error(
            f"Error getting nested attribute {attr} from {obj} - Returning default value: {default} - Error: {e}"
        )
        return default


class DefaultColumnRenderingConfig(BaseSettings):
    """
    Default column configuration.

    This is used to configure the default column configuration for the table.
    """

    color: str = Field(description="The color of the column", default="blue")
    bgcolor: Optional[str] = Field(
        description="The background color of the column", default=None
    )
    bold: bool = Field(description="Whether to bold the column", default=False)
    dim: bool = Field(description="Whether to dim the column", default=False)
    italic: bool = Field(description="Whether to italic the column", default=False)
    underline: bool = Field(
        description="Whether to underline the column", default=False
    )
    blink: bool = Field(description="Whether to blink the column", default=False)
    no_wrap: bool = Field(description="Whether to wrap the column", default=False)
    justify: JustifyMethod = Field(
        description="The justification of the column", default="left"
    )

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "DEFAULT_COLUMN_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class Column(BaseModel):
    """
    Represents the structure of a table column.

    Note: This is a low-level data model. To ensure that user-defined
    styling and configurations are applied, you should always create
    instances using the `get_column()` factory function instead of
    instantiating this class directly.
    """

    header: str = Field(..., description="The header of the column")
    no_wrap: bool = Field(..., description="Whether to wrap the column")
    justify: JustifyMethod = Field(..., description="The justification of the column")
    style: StyleType = Field(
        ...,
        description="The style of the column. See rich.style.Style for more details.",
    )
    value_formatter: Callable[[Any], str] = Field(
        ...,
        description="A function to format the value of the column",
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class TableRenderContext(BaseRenderContext):
    """Render context for table output."""

    header_style: str = Field(..., description="The header style of the table")
    border_style: str = Field(..., description="The border style of the table")

    default_no_wrap: bool = Field(..., description="Whether to wrap the column")
    default_justify: JustifyMethod = Field(
        ..., description="The justification of the column"
    )
    default_style: StyleType = Field(..., description="The style of the column")

    columns: Dict[str, Column] = Field(..., description="The columns to display")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def get_column(
        header: str,
        no_wrap: Optional[bool] = None,
        justify: Optional[JustifyMethod] = None,
        style: Optional[StyleType] = None,
        value_formatter: Callable[[Any], str] = lambda x: (
            str(x) if x is not None else ""
        ),
    ) -> Column:
        """
        Get a column with default styling based on the header.
        """
        style_config = DefaultColumnRenderingConfig()

        final_no_wrap = no_wrap or style_config.no_wrap
        final_justify = justify or style_config.justify

        final_style = style or Style(
            color=style_config.color,
            bgcolor=style_config.bgcolor,
            bold=style_config.bold,
            dim=style_config.dim,
            italic=style_config.italic,
            underline=style_config.underline,
            blink=style_config.blink,
        )

        return Column(
            header=header,
            no_wrap=final_no_wrap,
            justify=final_justify,
            style=final_style,
            value_formatter=value_formatter,
        )

    @classmethod
    def columns_from_model_dump(cls, data: Dict[str, Any]) -> Dict[str, Column]:
        """
        Get the columns from a model dump.
        """
        return {key: cls.get_column(header=key) for key in data.keys()}

    @classmethod
    def get_table_render_context(
        cls,
        columns: Dict[str, Column],
        header_style: Optional[str] = None,
        border_style: Optional[str] = None,
        default_no_wrap: Optional[bool] = None,
        default_justify: Optional[JustifyMethod] = None,
        default_style: Optional[StyleType] = None,
    ) -> TableRenderContext:
        style_config = DefaultTableRenderingConfig()
        return cls(
            header_style=header_style or style_config.header_style,
            border_style=border_style or style_config.border_style,
            default_no_wrap=default_no_wrap or style_config.default_no_wrap,
            default_justify=default_justify or style_config.default_justify,
            default_style=default_style or style_config.default_style,
            columns=columns,
        )


class DefaultTableRenderingConfig(BaseSettings):
    """
    Table configuration.
    """

    header_style: str = Field(
        description="The header style of the table", default="bold"
    )
    border_style: str = Field(
        description="The border style of the table", default="custom"
    )

    default_no_wrap: bool = Field(
        description="Whether to wrap the column", default=False
    )
    default_justify: JustifyMethod = Field(
        description="The justification of the column", default="left"
    )
    default_style: StyleType = Field(
        description="The style of the column", default=Style()
    )

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "TABLE_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    def to_table_render_context(self, columns: Dict[str, Column]) -> TableRenderContext:
        """Convert the rendering config to a table render context."""
        return TableRenderContext(
            header_style=self.header_style,
            border_style=self.border_style,
            default_no_wrap=self.default_no_wrap,
            default_justify=self.default_justify,
            default_style=self.default_style,
            columns=columns,
        )


class _BaseTableRenderer:
    """Base class for Table renderers."""

    def __init__(self):
        self.default_render_config = DefaultTableRenderingConfig()

    def resolve_context(
        self,
        render_context: Optional[BaseRenderContext],
        columns: Optional[Dict[str, Column]] = None,
    ) -> TableRenderContext:
        """Resolve the render context."""
        if render_context:
            assert isinstance(
                render_context, TableRenderContext
            ), "Render context must be a TableRenderContext"
            return render_context

        assert columns, "If no render context is provided, columns must be set"

        return self.default_render_config.to_table_render_context(columns)

    def _create_table(self, render_context: TableRenderContext) -> Table:
        """Create a configured Table instance."""
        table = Table(
            show_header=True,
            header_style=render_context.header_style,
            border_style=render_context.border_style,
        )
        return table


class TableListRenderer(IListRenderer[T, Table], Generic[T], _BaseTableRenderer):
    """Renders a list of items as a table."""

    def __init__(self):
        super().__init__()

    def render(
        self,
        data: Sequence[T],
        render_context: Optional[BaseRenderContext] = None,
    ) -> Table:
        """Render a list of items to a table."""
        if not data:
            return Table()

        columns = None
        if not render_context:
            # We fallback to the first item in the list to get the columns
            model_dump: Dict[str, Any] = data[0].model_dump()
            columns = TableRenderContext.columns_from_model_dump(model_dump)

        validated_render_context: TableRenderContext = self.resolve_context(
            render_context, columns
        )
        table: Table = self._create_table(validated_render_context)

        for key, column in validated_render_context.columns.items():
            table.add_column(
                validated_render_context.columns[key].header,
                justify=validated_render_context.columns[key].justify,
                no_wrap=validated_render_context.columns[key].no_wrap,
                style=validated_render_context.columns[key].style,
            )

        for item_data in data:
            row_values: List[str] = []
            for key, column in validated_render_context.columns.items():
                value: Any = _get_nested_attribute(item_data, key)
                column: Column = validated_render_context.columns[key]
                value = column.value_formatter(value)
                row_values.append(str(value))
            table.add_row(*row_values)

        return table


class TableSingleItemRenderer(
    ISingleItemRenderer[T, Table], Generic[T], _BaseTableRenderer
):
    """Renders a single item as a table."""

    def __init__(self):
        super().__init__()

    def render(
        self,
        data: T,
        render_context: Optional[BaseRenderContext] = None,
    ) -> Table:
        """Render the attributes of a single item as a two-column table (Property, Value)."""
        # Always use columns "Property" and "Value"
        columns = None
        if not render_context:
            column_property = TableRenderContext.get_column(
                header="Property", style=Style(color="blue", bold=True)
            )
            column_value = TableRenderContext.get_column(header="Value")
            columns = {
                "Property": column_property,
                "Value": column_value,
            }
        validated_render_context: TableRenderContext = self.resolve_context(
            render_context, columns
        )
        table = self._create_table(validated_render_context)

        table.add_column(
            validated_render_context.columns["Property"].header,
            justify=validated_render_context.columns["Property"].justify,
            no_wrap=validated_render_context.columns["Property"].no_wrap,
            style=validated_render_context.columns["Property"].style,
        )
        table.add_column(
            validated_render_context.columns["Value"].header,
            justify=validated_render_context.columns["Value"].justify,
            no_wrap=validated_render_context.columns["Value"].no_wrap,
            style=validated_render_context.columns["Value"].style,
        )

        attrs: Dict[str, Any] = data.model_dump()
        for key, value in attrs.items():
            property_column: Column = validated_render_context.columns["Property"]
            property: str = property_column.value_formatter(key)

            value_column: Column = validated_render_context.columns["Value"]
            value: str = value_column.value_formatter(value)
            table.add_row(property, value)
        return table

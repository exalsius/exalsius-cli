from __future__ import annotations

from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console, JustifyMethod
from rich.style import Style, StyleType
from rich.table import Table

from exalsius.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)
from exalsius.utils.theme import custom_theme

T = TypeVar("T")


class TableListRenderer(BaseListRenderer[T, str], Generic[T]):
    """Renders a list of items as a table."""

    def __init__(
        self,
        columns_rendering_map: Dict[str, Column],
        table_rendering_config: Optional[TableRenderingConfig] = None,
        console: Optional[Console] = None,
    ):
        self.columns_rendering_map: Dict[str, Column] = columns_rendering_map
        self.table_rendering_config: TableRenderingConfig = (
            table_rendering_config or TableRenderingConfig()
        )
        self.console: Console = console or Console(theme=custom_theme)

    def render(self, data: List[T]) -> None:
        """Render a list of items to a table."""
        if not data:
            self.console.print("No items to display.")
            return

        table = Table(
            show_header=True,
            header_style=self.table_rendering_config.header_style,
            border_style=self.table_rendering_config.border_style,
        )

        for key in self.columns_rendering_map.keys():
            table.add_column(
                self.columns_rendering_map[key].header,
                justify=self.columns_rendering_map[key].justify,
                no_wrap=self.columns_rendering_map[key].no_wrap,
                style=self.columns_rendering_map[key].style,
            )

        for item_data in data:
            row_values = [
                str(getattr(item_data, key, ""))
                for key in self.columns_rendering_map.keys()
            ]
            table.add_row(*row_values)

        self.console.print(table)


class TableSingleItemRenderer(BaseSingleItemRenderer[T, str], Generic[T]):
    """Renders a single item as a table."""

    def __init__(
        self,
        columns_map: Dict[str, Column],
        table_rendering_config: Optional[TableRenderingConfig] = None,
        console: Optional[Console] = None,
    ):
        self.columns_map: Dict[str, Column] = columns_map
        self.table_rendering_config: TableRenderingConfig = (
            table_rendering_config or TableRenderingConfig()
        )
        self.console: Console = console or Console(theme=custom_theme)

    def render(self, data: T) -> None:
        """Render a single item to a table."""
        table = Table(
            show_header=True,
            header_style=self.table_rendering_config.header_style,
            border_style=self.table_rendering_config.border_style,
        )
        table.add_column("Property", style="bold")
        table.add_column("Value")

        for key in self.columns_map.keys():
            value = str(getattr(data, key, ""))
            table.add_row(self.columns_map[key].header, value)

        self.console.print(table)


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


class DefaultColumnRenderingConfig(BaseSettings):
    """
    Default column configuration.

    This is used to configure the default column configuration for the table.
    """

    color: str = Field(description="The color of the column", default="blue")
    bgcolor: str = Field(
        description="The background color of the column", default="blue"
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


def get_column(
    header: str,
    no_wrap: Optional[bool] = None,
    justify: Optional[JustifyMethod] = None,
    style: Optional[StyleType] = None,
) -> Column:
    """
    Get a column with default styling based on the header.
    """
    style_config = DefaultColumnRenderingConfig()

    final_no_wrap = style_config.no_wrap if no_wrap is None else no_wrap
    final_justify = style_config.justify if justify is None else justify

    if style is None:
        style = Style(
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
        style=style,
    )


class TableRenderingConfig(BaseSettings):
    """
    Table configuration.
    """

    header_style: StyleType = Field(
        description="The header style of the table", default="bold"
    )
    border_style: StyleType = Field(
        description="The border style of the table", default="custom"
    )

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "TABLE_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )

from enum import StrEnum
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

from exls.shared.adapters.ui.display.render.json import JsonRenderContext
from exls.shared.adapters.ui.display.render.table import TableRenderContext
from exls.shared.adapters.ui.display.render.text import TextRenderContext
from exls.shared.adapters.ui.display.render.yaml import YamlRenderContext


class OutputFormat(StrEnum):
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"


# Type-safe format-context pairs
T_TableFormat = Literal[OutputFormat.TABLE]
T_JsonFormat = Literal[OutputFormat.JSON]
T_YamlFormat = Literal[OutputFormat.YAML]
T_TextFormat = Literal[OutputFormat.TEXT]

# Type-safe format-context union
FormatContextPair = Union[
    tuple[T_TableFormat, Optional[TableRenderContext]],
    tuple[T_JsonFormat, Optional[JsonRenderContext]],
    tuple[T_YamlFormat, Optional[YamlRenderContext]],
    tuple[T_TextFormat, Optional[TextRenderContext]],
]


class DisplayChoice(BaseModel):
    title: str = Field(..., description="The title of the choice.")
    value: Any = Field(default=None, description="The value of the choice.")
    disabled: Optional[str] = Field(
        default=None, description="The disabled state of the choice."
    )
    checked: bool = Field(default=False, description="The checked state of the choice.")

    @model_validator(mode="after")
    def set_default_value(self):
        if self.value is None:
            self.value = self.title
        return self

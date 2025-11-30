from enum import StrEnum
from typing import Literal, Optional, Union

from exls.shared.adapters.ui.output.render.json import JsonRenderContext
from exls.shared.adapters.ui.output.render.table import TableRenderContext
from exls.shared.adapters.ui.output.render.text import TextRenderContext
from exls.shared.adapters.ui.shared.render.render import YamlRenderContext


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

from typing import Dict, Optional, Union

from pydantic import BaseModel

from exls.shared.adapters.ui.output.render.json import JsonRenderContext
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.render.text import TextRenderContext
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.shared.render.render import YamlRenderContext


class ViewContext(BaseModel):
    """
    Holds rendering context for all supported output formats for a specific view.
    """

    ctx_table: Optional[TableRenderContext] = None
    ctx_json: Optional[JsonRenderContext] = None
    ctx_yaml: Optional[YamlRenderContext] = None
    ctx_text: Optional[TextRenderContext] = None

    @classmethod
    def from_table_columns(cls, columns: Dict[str, Column]) -> "ViewContext":
        """Helper to create a context with just table columns (common case)."""
        return cls(
            ctx_table=TableRenderContext.get_table_render_context(columns=columns)
        )

    def get_context_for_format(self, output_format: OutputFormat) -> Union[
        Optional[TableRenderContext],
        Optional[JsonRenderContext],
        Optional[YamlRenderContext],
        Optional[TextRenderContext],
    ]:
        if output_format == OutputFormat.TABLE:
            return self.ctx_table
        elif output_format == OutputFormat.JSON:
            return self.ctx_json
        elif output_format == OutputFormat.YAML:
            return self.ctx_yaml
        elif output_format == OutputFormat.TEXT:
            return self.ctx_text

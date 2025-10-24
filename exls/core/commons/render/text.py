from typing import List, Optional

from pydantic import BaseModel, Field

from exls.core.base.display import ErrorDisplayModel
from exls.core.base.render import BaseSingleItemRenderer


class TextRenderConfig(BaseModel):
    """Rich Text Render configuration."""

    color: str = Field(default="white", description="The color of the text")
    bgcolor: Optional[str] = Field(
        default=None, description="The background color of the text"
    )
    bold: bool = Field(default=False, description="Whether to bold the text")
    dim: bool = Field(default=False, description="Whether to dim the text")
    italic: bool = Field(default=False, description="Whether to italic the text")
    underline: bool = Field(default=False, description="Whether to underline the text")
    blink: bool = Field(default=False, description="Whether to blink the text")


class _BaseRichTextRenderer:
    """Base rich text renderer."""

    def __init__(
        self,
        render_config: Optional[TextRenderConfig] = None,
    ):
        self.render_config = render_config or TextRenderConfig()

    def _get_style_parts(self) -> List[str]:
        style_parts: List[str] = []
        if self.render_config.bold:
            style_parts.append("bold")
        if self.render_config.dim:
            style_parts.append("dim")
        if self.render_config.italic:
            style_parts.append("italic")
        if self.render_config.underline:
            style_parts.append("underline")
        if self.render_config.blink:
            style_parts.append("blink")

        style_parts.append(self.render_config.color)

        if self.render_config.bgcolor:
            style_parts.append(f"on {self.render_config.bgcolor}")

        return style_parts

    def _get_styled_text(self, text: str) -> str:
        style_parts = self._get_style_parts()
        if not style_parts:
            return text
        return f"[{' '.join(style_parts)}]{text}[/]"


class RichTextRenderer(_BaseRichTextRenderer, BaseSingleItemRenderer[str, str]):
    """Render a single item as a text string."""

    def __init__(
        self,
        render_config: Optional[TextRenderConfig] = None,
    ):
        self.render_config = render_config or TextRenderConfig(color="white")

    def render(self, data: str) -> str:
        return self._get_styled_text(data)


class RichTextErrorMessageRenderer(
    _BaseRichTextRenderer, BaseSingleItemRenderer[ErrorDisplayModel, str]
):
    """Render an error message as a rich text string."""

    def __init__(
        self,
        render_config: Optional[TextRenderConfig] = None,
    ):
        self.render_config = render_config or TextRenderConfig(color="red")

    def render(self, data: ErrorDisplayModel) -> str:
        message = data.message
        parts: List[str] = []
        parts.append(message)
        return self._get_styled_text(" - ".join(parts))


class RichTextSuccessMessageRenderer(
    _BaseRichTextRenderer, BaseSingleItemRenderer[str, str]
):
    """Render a success message as a rich text string."""

    def __init__(
        self,
        render_config: Optional[TextRenderConfig] = None,
    ):
        self.render_config = render_config or TextRenderConfig(color="green")

    def render(self, data: str) -> str:
        return self._get_styled_text(data)

from __future__ import annotations

from typing import List, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field

from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.output.render.entities import TextMessageItem
from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext

T = TypeVar("T", bound=BaseModel)


class DefaultTextRenderConfig(BaseModel):
    """Default rich text render configuration."""

    color: str = Field(default="white", description="The color of the text")
    bgcolor: Optional[str] = Field(
        default=None, description="The background color of the text"
    )
    bold: bool = Field(default=False, description="Whether to bold the text")
    dim: bool = Field(default=False, description="Whether to dim the text")
    italic: bool = Field(default=False, description="Whether to italic the text")
    underline: bool = Field(default=False, description="Whether to underline the text")
    blink: bool = Field(default=False, description="Whether to blink the text")

    def to_text_render_context(self) -> TextRenderContext:
        return TextRenderContext(
            color=self.color,
            bgcolor=self.bgcolor,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            blink=self.blink,
        )


class DefaultSuccessTextRenderConfig(DefaultTextRenderConfig):
    """Default success rich text render configuration."""

    color: str = Field(default="green", description="The color of the text")


class DefaultErrorMessageTextRenderConfig(DefaultTextRenderConfig):
    """Default error rich text render configuration."""

    color: str = Field(default="red", description="The color of the text")


class TextRenderContext(BaseRenderContext):
    """Render context for text output."""

    color: str = Field(..., description="The color of the text")
    bgcolor: Optional[str] = Field(..., description="The background color of the text")
    bold: bool = Field(..., description="Whether to bold the text")
    dim: bool = Field(..., description="Whether to dim the text")
    italic: bool = Field(..., description="Whether to italic the text")
    underline: bool = Field(..., description="Whether to underline the text")
    blink: bool = Field(..., description="Whether to blink the text")


class _BaseRichTextRenderer:
    """Base rich text renderer."""

    def __init__(self, default_config: Optional[DefaultTextRenderConfig] = None):
        self.default_render_config = default_config or DefaultTextRenderConfig()

    def resolve_context(
        self, render_context: Optional[BaseRenderContext]
    ) -> TextRenderContext:
        """Resolve the render context."""
        assert isinstance(
            render_context, (TextRenderContext, type(None))
        ), "Render context must be a TextRenderContext"
        return (
            render_context
            if render_context
            else self.default_render_config.to_text_render_context()
        )

    def _get_style_parts(self, render_context: TextRenderContext) -> List[str]:
        style_parts: List[str] = []
        if render_context.bold:
            style_parts.append("bold")
        if render_context.dim:
            style_parts.append("dim")
        if render_context.italic:
            style_parts.append("italic")
        if render_context.underline:
            style_parts.append("underline")
        if render_context.blink:
            style_parts.append("blink")

        style_parts.append(render_context.color)

        if render_context.bgcolor:
            style_parts.append(f"on {render_context.bgcolor}")

        return style_parts

    def _get_styled_text(self, text: str, render_context: TextRenderContext) -> str:
        style_parts = self._get_style_parts(render_context)
        if not style_parts:
            return text
        return f"[{' '.join(style_parts)}]{text}[/]"


class RichTextListRenderer(_BaseRichTextRenderer, IListRenderer[T, str]):
    """Render a list of items as a text string."""

    def __init__(self, render_config: Optional[DefaultTextRenderConfig] = None):
        super().__init__(render_config or DefaultTextRenderConfig())

    def render(
        self, data: Sequence[T], render_context: Optional[BaseRenderContext] = None
    ) -> str:
        validated_render_context = self.resolve_context(render_context)
        return "\n".join(
            self._get_styled_text(str(item), validated_render_context) for item in data
        )


class RichTextItemRenderer(_BaseRichTextRenderer, ISingleItemRenderer[T, str]):
    """Render a single item as a text string."""

    def __init__(self, render_config: Optional[DefaultTextRenderConfig] = None):
        super().__init__(render_config)

    def render(
        self, data: T, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        validated_render_context = self.resolve_context(render_context)
        return self._get_styled_text(str(data), validated_render_context)


class RichTextInfoMessageRenderer(RichTextItemRenderer[TextMessageItem]):
    """Render a single item as a text string."""

    def __init__(self, render_config: Optional[DefaultTextRenderConfig] = None):
        super().__init__(render_config or DefaultTextRenderConfig())

    def render(
        self, data: TextMessageItem, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        validated_render_context = self.resolve_context(render_context)
        return self._get_styled_text(data.message, validated_render_context)


class RichTextSuccessMessageRenderer(RichTextItemRenderer[TextMessageItem]):
    """Render a success message as a rich text string."""

    def __init__(self, render_config: Optional[DefaultSuccessTextRenderConfig] = None):
        super().__init__(render_config or DefaultSuccessTextRenderConfig())

    def render(
        self, data: TextMessageItem, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        validated_render_context = self.resolve_context(render_context)
        return self._get_styled_text(data.message, validated_render_context)


class RichTextErrorMessageRenderer(RichTextItemRenderer[TextMessageItem]):
    """Render an error message as a rich text string."""

    def __init__(
        self, render_config: Optional[DefaultErrorMessageTextRenderConfig] = None
    ):
        super().__init__(render_config or DefaultErrorMessageTextRenderConfig())

    def render(
        self, data: TextMessageItem, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        validated_render_context = self.resolve_context(render_context)
        return self._get_styled_text(data.message, validated_render_context)

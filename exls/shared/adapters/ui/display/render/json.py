from __future__ import annotations

import json
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel, Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

from exls.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.shared.adapters.ui.display.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.display.render.entities import BaseRenderContext

T = TypeVar("T", bound=BaseModel)


class JsonRenderConfig(BaseSettings):
    """Render configuration."""

    default_indent: int = 4

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "JSON_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )

    def to_json_render_context(self) -> JsonRenderContext:
        return JsonRenderContext(indent=self.default_indent)


class JsonRenderContext(BaseRenderContext):
    """Render context for JSON output."""

    indent: PositiveInt = Field(
        ..., description="The number of spaces to use for indentation."
    )


class _BaseJsonRenderer:
    """Base class for JSON renderers."""

    def __init__(self):
        self.default_render_config = JsonRenderConfig()

    def resolve_context(
        self, render_context: Optional[BaseRenderContext]
    ) -> JsonRenderContext:
        """Resolve the render context."""
        if render_context:
            assert isinstance(render_context, JsonRenderContext), (
                "Render context must be a JsonRenderContext"
            )
        return (
            render_context
            if render_context
            else self.default_render_config.to_json_render_context()
        )

    def _format_json(
        self,
        data: Dict[str, Any] | List[Dict[str, Any]],
        render_context: JsonRenderContext,
    ) -> str:
        """Format data as a JSON string."""
        return json.dumps(data, indent=render_context.indent, default=str)


class _BaseJsonStringRenderer(Generic[T], _BaseJsonRenderer):
    """Base class for JSON renderers dealing with Pydantic models."""

    def _process_item(self, item: T) -> Dict[str, Any]:
        """Process a single Pydantic model item."""
        return item.model_dump()


class JsonSingleItemStringRenderer(
    _BaseJsonStringRenderer[T], ISingleItemRenderer[T, str]
):
    """Renders a single item as a JSON string."""

    def render(
        self, data: T, render_context: Optional[BaseRenderContext] = None
    ) -> str:
        """Render a single item DTO to JSON."""
        validated_render_context = self.resolve_context(render_context)

        processed_payload: Dict[str, Any] = self._process_item(data)
        json_string = self._format_json(processed_payload, validated_render_context)
        return json_string


class JsonListStringRenderer(_BaseJsonStringRenderer[T], IListRenderer[T, str]):
    """Renders a list of items as a JSON string."""

    def render(
        self, data: Sequence[T], render_context: Optional[BaseRenderContext] = None
    ) -> str:
        """Render a list of items to JSON."""
        validated_render_context = self.resolve_context(render_context)

        processed_payload: List[Dict[str, Any]] = [
            self._process_item(item) for item in data
        ]
        json_string = self._format_json(processed_payload, validated_render_context)
        return json_string

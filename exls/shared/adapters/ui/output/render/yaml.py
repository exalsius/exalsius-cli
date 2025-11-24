from __future__ import annotations

from io import StringIO
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from exls.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.output.render.entities import BaseRenderContext

T = TypeVar("T", bound=BaseModel)


class YamlRenderContext(BaseRenderContext):
    """Render context for YAML output."""

    indent: int = Field(..., description="Indentation level")
    comments: Optional[Dict[str, str]] = Field(
        default=None, description="Comments to add to the YAML"
    )


class DefaultYamlRenderConfig(BaseSettings):
    """Render configuration."""

    indent: int = 2

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "YAML_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )

    def to_yaml_render_context(self) -> YamlRenderContext:
        return YamlRenderContext(indent=self.indent)


class _BaseYamlRenderer:
    """Base class for YAML renderers."""

    def __init__(self):
        self.default_render_config = DefaultYamlRenderConfig()

    def resolve_context(
        self, render_context: Optional[BaseRenderContext]
    ) -> YamlRenderContext:
        """Resolve the render context."""
        assert isinstance(
            render_context, (YamlRenderContext, type(None))
        ), "Render context must be a YamlRenderContext"
        return (
            render_context
            if render_context
            else self.default_render_config.to_yaml_render_context()
        )

    def _dump_yaml(self, data: Any, render_context: YamlRenderContext) -> str:
        """Dump data to a YAML string."""
        yaml = YAML()
        yaml.indent(  # type: ignore
            mapping=render_context.indent,
            sequence=render_context.indent * 2,
            offset=render_context.indent,
        )
        string_stream = StringIO()
        yaml.dump(data, stream=string_stream)  # type: ignore
        return string_stream.getvalue()


class _BaseYamlStringRenderer(Generic[T], _BaseYamlRenderer):
    """Base class for YAML renderers dealing with Pydantic models."""

    def _process_item(
        self, item: T, comments: Optional[Dict[str, str]] = None
    ) -> CommentedMap:
        """Process a single Pydantic model item."""
        data: Dict[str, Any] = item.model_dump()

        commented_data: CommentedMap = CommentedMap()
        for key, value in data.items():
            commented_data[key] = value
            if comments and key in comments:
                commented_data.yaml_set_comment_before_after_key(  # type: ignore
                    key, before=f"{comments[key]}"
                )
        return commented_data

    def format_yaml(self, data: T, render_context: YamlRenderContext) -> str:
        """Format a dictionary as a YAML string."""

        processed_payload: CommentedMap = self._process_item(
            data, render_context.comments
        )
        return self._dump_yaml(processed_payload, render_context)


class YamlSingleItemStringRenderer(
    _BaseYamlStringRenderer[T], ISingleItemRenderer[T, str]
):
    """Renders a single item as a YAML string."""

    def __init__(self):
        super().__init__()

    def render(
        self,
        data: T,
        render_context: Optional[BaseRenderContext] = None,
    ) -> str:
        """Render a single item DTO to YAML."""
        validated_render_context = self.resolve_context(render_context)

        yaml_string: str = self.format_yaml(data, validated_render_context)
        return yaml_string


class YamlListStringRenderer(_BaseYamlStringRenderer[T], IListRenderer[T, str]):
    """Renders a list of items as a YAML string."""

    def __init__(self):
        super().__init__()

    def render(
        self,
        data: Sequence[T],
        render_context: Optional[BaseRenderContext] = None,
    ) -> str:
        """Render a list of items to YAML."""
        validated_render_context = self.resolve_context(render_context)

        yaml_string = "\n".join(
            self.format_yaml(item, validated_render_context) for item in data
        )
        return yaml_string

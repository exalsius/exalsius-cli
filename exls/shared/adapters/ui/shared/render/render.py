from __future__ import annotations

from io import StringIO
from typing import (
    Any,
    Dict,
    Optional,
    cast,
)

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from exls.defaults import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext


class YamlRenderContext(BaseRenderContext):
    """Render context for YAML output."""

    indent: int = Field(..., description="Indentation level")
    comments: Optional[Dict[str, str]] = Field(
        default=None, description="Comments to add to the YAML"
    )


class BaseYamlRenderConfig(BaseSettings):
    """Base render configuration for YAML."""

    indent: int = 2

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "YAML_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )

    def to_yaml_render_context(self) -> YamlRenderContext:
        return YamlRenderContext(indent=self.indent)


class DictToYamlStringRenderer:
    """Renderer for converting dictionaries to YAML strings."""

    def __init__(self, default_render_config: Optional[BaseYamlRenderConfig] = None):
        self._default_render_config: BaseYamlRenderConfig = (
            default_render_config if default_render_config else BaseYamlRenderConfig()
        )

    def _resolve_context(
        self, render_context: Optional[YamlRenderContext]
    ) -> YamlRenderContext:
        """Resolve the render context."""
        if not render_context:
            return self._default_render_config.to_yaml_render_context()
        return render_context

    def _process_item(
        self,
        data: Dict[str, Any],
        comments: Optional[Dict[str, str]] = None,
        parent_path: str = "",
    ) -> CommentedMap:
        """Process a single Pydantic model item."""

        commented_data: CommentedMap = CommentedMap()
        for key, value in data.items():
            current_path = f"{parent_path}.{key}" if parent_path else key

            if isinstance(value, dict):
                commented_data[key] = self._process_item(
                    cast(Dict[str, Any], value), comments, parent_path=current_path
                )
            else:
                commented_data[key] = value

            if comments and current_path in comments:
                commented_data.yaml_set_comment_before_after_key(  # type: ignore
                    key, before=f"{comments[current_path]}"
                )
        return commented_data

    def _dump_yaml(self, data: CommentedMap, render_context: YamlRenderContext) -> str:
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

    def format_yaml(
        self, data: Dict[str, Any], render_context: Optional[YamlRenderContext] = None
    ) -> str:
        """Format a dictionary as a YAML string."""
        validated_render_context: YamlRenderContext = self._resolve_context(
            render_context=render_context
        )
        processed_payload: CommentedMap = self._process_item(
            data,
            (
                validated_render_context.comments
                if validated_render_context.comments
                else None
            ),
        )
        return self._dump_yaml(processed_payload, validated_render_context)

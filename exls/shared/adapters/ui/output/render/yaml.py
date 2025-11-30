from __future__ import annotations

from typing import (
    Any,
    Dict,
    Optional,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from exls.defaults import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.shared.adapters.ui.output.interfaces import (
    IListRenderer,
    ISingleItemRenderer,
)
from exls.shared.adapters.ui.shared.render.entities import BaseRenderContext
from exls.shared.adapters.ui.shared.render.render import (
    BaseYamlRenderConfig,
    DictToYamlStringRenderer,
    YamlRenderContext,
)

T = TypeVar("T", bound=BaseModel)


class YamlObjectOutputRenderConfig(BaseYamlRenderConfig):
    """Configuration for the YAML object output renderer."""

    indent: int = 2

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "YAML_OBJECT_OUTPUT_RENDER_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class YamlSingleItemStringRenderer(
    DictToYamlStringRenderer, ISingleItemRenderer[T, str]
):
    """Renders a single item as a YAML string."""

    def __init__(self, render_config: Optional[BaseYamlRenderConfig] = None):
        super().__init__(render_config or YamlObjectOutputRenderConfig())

    def render(
        self,
        data: T,
        render_context: Optional[BaseRenderContext] = None,
    ) -> str:
        """Render a single item DTO to YAML."""
        assert isinstance(
            render_context, YamlRenderContext or None
        ), "Render context must be a YamlRenderContext"
        data_dict: Dict[str, Any] = data.model_dump()

        yaml_string: str = self.format_yaml(data_dict, render_context)
        return yaml_string


class YamlListStringRenderer(DictToYamlStringRenderer, IListRenderer[T, str]):
    """Renders a list of items as a YAML string."""

    def __init__(self, render_config: Optional[BaseYamlRenderConfig] = None):
        super().__init__(render_config or YamlObjectOutputRenderConfig())

    def render(
        self,
        data: Sequence[T],
        render_context: Optional[BaseRenderContext] = None,
    ) -> str:
        """Render a list of items to YAML."""
        assert isinstance(
            render_context, YamlRenderContext or None
        ), "Render context must be a YamlRenderContext"
        yaml_string = "\n".join(
            self.format_yaml(item.model_dump(), render_context) for item in data
        )
        return yaml_string

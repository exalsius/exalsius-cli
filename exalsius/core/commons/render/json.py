import json
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)

T = TypeVar("T", bound=BaseModel)


class JsonRenderConfig(BaseSettings):
    """Render configuration."""

    indent: int = 4

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "JSON_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class _BaseJsonStringRenderer(Generic[T]):
    """Base class for JSON renderers."""

    def __init__(
        self,
        render_config: Optional[JsonRenderConfig] = None,
    ):
        self.render_config = render_config or JsonRenderConfig()

    def _process_item(self, item: T) -> Dict[str, Any]:
        """Process a single Pydantic model item."""
        return item.model_dump()

    def _format_json(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """Format a dictionary as a JSON string."""
        return json.dumps(data, indent=self.render_config.indent, default=str)


class JsonSingleItemStringRenderer(
    _BaseJsonStringRenderer[T], BaseSingleItemRenderer[T, str]
):
    """Renders a single item as a JSON string."""

    def render(self, data: T) -> str:
        """Render a single item DTO to JSON."""
        processed_payload: Dict[str, Any] = self._process_item(data)
        json_string = self._format_json(processed_payload)
        return json_string


class JsonListStringRenderer(_BaseJsonStringRenderer[T], BaseListRenderer[T, str]):
    """Renders a list of items as a JSON string."""

    def render(self, data: List[T]) -> str:
        """Render a list of items to JSON."""
        processed_payload: List[Dict[str, Any]] = [
            self._process_item(item) for item in data
        ]
        json_string = self._format_json(processed_payload)
        return json_string


class JsonMessageRenderer(BaseSingleItemRenderer[str, str]):
    """Renders any python type as a JSON string."""

    def __init__(
        self,
        render_config: Optional[JsonRenderConfig] = None,
        message_key: str = "message",
    ):
        self.render_config: JsonRenderConfig = render_config or JsonRenderConfig()
        self.message_key: str = message_key

    def _format_json(self, data: Any) -> str:
        """Format a dictionary as a JSON string."""
        return json.dumps(data, indent=self.render_config.indent, default=str)

    def render(self, data: str) -> str:
        """Render a single item DTO to JSON."""
        json_string = self._format_json({self.message_key: data})
        return json_string

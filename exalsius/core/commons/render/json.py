import json
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
)

from pydantic import BaseModel
from pydantic.alias_generators import to_camel, to_snake
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.json import JSON

from exalsius.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)
from exalsius.utils.theme import custom_theme

KeyFormatter = Callable[[str], str]
KeyFormat = Literal["snake", "camel", "lower"]


FORMATTERS: Dict[KeyFormat, KeyFormatter] = {
    "snake": to_snake,
    "camel": to_camel,
    "lower": str.lower,
}

T = TypeVar("T", bound=BaseModel)


class JsonRenderConfig(BaseSettings):
    """Render configuration."""

    indent: int = 4

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "JSON_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class _BaseJsonRenderer(Generic[T]):
    """Base class for JSON renderers."""

    def __init__(
        self,
        console: Optional[Console] = None,
        render_config: Optional[JsonRenderConfig] = None,
    ):
        self.console = console or Console(theme=custom_theme)
        self.render_config = render_config or JsonRenderConfig()

    def _process_item(self, item: T) -> Dict[str, Any]:
        """Process a single Pydantic model item."""
        return item.model_dump()

    def _format_json(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """Format a dictionary as a JSON string."""
        return json.dumps(data, indent=self.render_config.indent, default=str)

    def _print_json(self, json_string: str) -> None:
        """Print a JSON string."""
        self.console.print(JSON(json_string))


class JsonSingleItemRenderer(_BaseJsonRenderer[T], BaseSingleItemRenderer[T, str]):
    """Renders a single item as a JSON string."""

    def render(self, data: T) -> None:
        """Render a single item DTO to JSON."""
        processed_payload: Dict[str, Any] = self._process_item(data)
        json_string = self._format_json(processed_payload)
        self._print_json(json_string)


class JsonListRenderer(_BaseJsonRenderer[T], BaseListRenderer[T, str]):
    """Renders a list of items as a JSON string."""

    def render(self, data: List[T]) -> None:
        """Render a list of items to JSON."""
        processed_payload: List[Dict[str, Any]] = [
            self._process_item(item) for item in data
        ]
        json_string = self._format_json(processed_payload)
        self._print_json(json_string)


class JsonMessageRenderer(BaseSingleItemRenderer[str, str]):
    """Renders any python type as a JSON string."""

    def __init__(
        self,
        console: Optional[Console] = None,
        render_config: Optional[JsonRenderConfig] = None,
        message_key: str = "message",
    ):
        self.console: Console = console or Console(theme=custom_theme)
        self.render_config: JsonRenderConfig = render_config or JsonRenderConfig()
        self.message_key: str = message_key

    def _format_json(self, data: Any) -> str:
        """Format a dictionary as a JSON string."""
        return json.dumps(data, indent=self.render_config.indent, default=str)

    def _print_json(self, json_string: str) -> None:
        """Print a JSON string."""
        self.console.print(JSON(json_string))

    def render(self, data: str) -> None:
        """Render a single item DTO to JSON."""
        json_string = self._format_json({self.message_key: data})
        self._print_json(json_string)

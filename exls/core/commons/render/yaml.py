from io import StringIO
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
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from exls.config import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
)

T = TypeVar("T", bound=BaseModel)


class YamlRenderConfig(BaseSettings):
    """Render configuration."""

    indent: int = 2

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "YAML_RENDERING_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class _BaseYamlStringRenderer(Generic[T]):
    """Base class for YAML renderers."""

    def __init__(
        self,
        render_config: Optional[YamlRenderConfig] = None,
    ):
        self.render_config: YamlRenderConfig = render_config or YamlRenderConfig()
        self.yaml: YAML = YAML()
        self.yaml.indent(  # type: ignore
            mapping=self.render_config.indent,
            sequence=self.render_config.indent * 2,
            offset=self.render_config.indent,
        )

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

    def _format_yaml(self, data: Union[List[Any], Any]) -> str:
        """Format a dictionary as a YAML string."""
        string_stream = StringIO()
        self.yaml.dump(data, stream=string_stream)  # type: ignore
        return string_stream.getvalue()


class YamlSingleItemStringRenderer(
    _BaseYamlStringRenderer[T], BaseSingleItemRenderer[T, str]
):
    """Renders a single item as a YAML string."""

    # TODO: The additional comments parameter breaks the Liskov Substitution Principle. We need to refactor this.

    def render(self, data: T, comments: Optional[Dict[str, str]] = None) -> str:
        """Render a single item DTO to YAML."""
        processed_payload: CommentedMap = self._process_item(data, comments)
        yaml_string: str = self._format_yaml(processed_payload)
        return yaml_string


class YamlListStringRenderer(_BaseYamlStringRenderer[T], BaseListRenderer[T, str]):
    """Renders a list of items as a YAML string."""

    def render(
        self,
        data: List[T],
        comments: Optional[Dict[str, str]] = None,
    ) -> str:
        """Render a list of items to YAML."""
        processed_payload = [self._process_item(item, comments) for item in data]
        yaml_string = self._format_yaml(processed_payload)
        return yaml_string


class YamlMessageRenderer(BaseSingleItemRenderer[str, str]):
    """Renders any python type as a YAML string."""

    def __init__(
        self,
        render_config: Optional[YamlRenderConfig] = None,
        message_key: str = "message",
    ):
        self.render_config: YamlRenderConfig = render_config or YamlRenderConfig()
        self.message_key: str = message_key
        self.yaml: YAML = YAML()
        self.yaml.indent(  # type: ignore
            mapping=self.render_config.indent,
            sequence=self.render_config.indent * 2,
            offset=self.render_config.indent,
        )

    def _format_yaml(self, data: Any) -> str:
        """Format a dictionary as a YAML string."""
        string_stream = StringIO()
        self.yaml.dump(data, stream=string_stream)  # type: ignore
        return string_stream.getvalue()

    def render(self, data: str) -> str:
        """Render a single item DTO to YAML."""
        yaml_string = self._format_yaml({self.message_key: data})
        return yaml_string

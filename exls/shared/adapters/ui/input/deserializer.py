from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, cast

from ruamel.yaml import YAML, YAMLError

from exls.shared.core.domain import ExalsiusError


class DeserializationError(ExalsiusError):
    pass


class InvalidYamlFormatError(DeserializationError):
    pass


class BaseToDictionaryDeserializer(ABC):
    @abstractmethod
    def deserialize(self, data: str) -> Dict[str, Any]: ...


class YamlStringToDictionaryDeserializer(BaseToDictionaryDeserializer):
    def deserialize(self, data: str) -> Dict[str, Any]:
        yaml = YAML(typ="safe")
        try:
            data_dict: Dict[str, Any] = cast(
                Dict[str, Any],
                yaml.load(stream=StringIO(data)),  # type: ignore
            )
        except YAMLError as e:
            raise InvalidYamlFormatError(f"Invalid YAML format: {e}") from e
        except Exception as e:
            raise DeserializationError(f"Failed to deserialize YAML: {e}") from e

        return data_dict

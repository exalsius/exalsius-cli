from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from exalsius.core.base.models import DeserializationError


class BaseCommand(ABC):
    """Base command with generic return type."""

    def _deserialize(self, raw_data: Dict[str, Any], model: Type[Any]) -> Any:
        try:
            return model(**raw_data)
        except Exception as e:
            raise DeserializationError(
                f"Failed to deserialize response {raw_data} with error {e}"
            )

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command and return a Pydantic model or error."""
        pass

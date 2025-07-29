from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel

from exalsius.core.base.models import DeserializationError

T = TypeVar("T", bound=BaseModel)


class BaseCommand(ABC, Generic[T]):
    """Base command with generic return type."""

    def _deserialize(self, raw_data: Dict[str, Any], model: Type[T]) -> T:
        try:
            return model(**raw_data)
        except Exception as e:
            raise DeserializationError(
                f"Failed to deserialize response {raw_data} with error {e}"
            )

    @abstractmethod
    def execute(self) -> T:
        """Execute the command and return a Pydantic model or error."""
        pass

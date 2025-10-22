from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ValidationError

from exls.core.base.deserializer import BaseDeserializer
from exls.core.base.exceptions import ExalsiusError

T_SerOutput = TypeVar("T_SerOutput", bound=BaseModel)


class DeserializationError(ExalsiusError):
    def __init__(
        self,
        source_data: Dict[str, Any],
        target_model_name: str,
        error_message: str,
    ):
        super().__init__(error_message)
        self.source_data = source_data
        self.target_model_name = target_model_name
        self.error_message = error_message

    def __str__(self) -> str:
        return f"DeserializationError: failed to deserialize {self.target_model_name} from {self.source_data}: {self.error_message}"


class PydanticDeserializer(BaseDeserializer[Dict[str, Any], T_SerOutput]):
    """Deserializes JSON to Pydantic models."""

    def deserialize(
        self, raw_data: Dict[str, Any], model: Type[T_SerOutput]
    ) -> T_SerOutput:
        try:
            return model.model_validate(raw_data)
        except ValidationError as e:
            raise DeserializationError(
                raw_data,
                model.__name__,
                f"Failed to deserialize {model.__name__}: {str(e)}",
            ) from e

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class BaseRequestDTO(BaseModel):
    """Base request DTO that commands receive and use internally to perform commands."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DeserializationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

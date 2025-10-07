from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseRequestDTO(BaseModel):
    """Base request DTO that commands receive and use internally to perform commands."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseCommand(Generic[T], ABC):
    @abstractmethod
    def execute(self) -> T | None:
        raise NotImplementedError

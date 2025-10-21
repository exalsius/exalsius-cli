from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exalsius.core.base.exceptions import ExalsiusError

T = TypeVar("T")


class CommandError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class BaseCommand(Generic[T], ABC):
    @abstractmethod
    def execute(self) -> T:
        raise NotImplementedError

from abc import ABC, abstractmethod
from ast import List
from typing import Generic, Optional, Tuple, TypeVar

T = TypeVar("T")


class BaseOperation(ABC, Generic[T]):
    """Base operation with generic return type."""

    @abstractmethod
    def execute(self) -> Tuple[Optional[T], Optional[str]]:
        """Execute the operation and return a Pydantic model or error."""
        pass


class ListOperation(BaseOperation[List]):
    """Base operation for listing resources."""

    @abstractmethod
    def execute(self) -> Tuple[Optional[List], Optional[str]]:
        pass


class BooleanOperation(BaseOperation[bool]):
    """Base operation for operations that return success/failure status."""

    @abstractmethod
    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the operation and return success status and optional error message.

        Returns:
            Tuple[bool, Optional[str]]: A tuple containing:
                - bool: True if operation succeeded, False if failed
                - Optional[str]: Error message if operation failed, None if succeeded
        """
        pass

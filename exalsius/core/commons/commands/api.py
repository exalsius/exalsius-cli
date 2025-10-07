from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from exalsius_api_client.exceptions import ApiException

from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.exceptions import ExalsiusError

T_API_Type = TypeVar("T_API_Type")
T_Return_Type = TypeVar("T_Return_Type")


class ExalsiusAPICommandError(ExalsiusError):
    def __init__(
        self, message: str, status: Optional[int] = None, reason: Optional[str] = None
    ):
        super().__init__(message)
        self.message: str = message
        self.status: Optional[int] = status
        self.reason: Optional[str] = reason

    def __str__(self):
        return self.message


class ExalsiusAPICommand(
    BaseCommand[T_Return_Type], Generic[T_API_Type, T_Return_Type]
):
    def __init__(self, api_client: T_API_Type):
        self._api_client: T_API_Type = api_client

    @property
    def api_client(self) -> T_API_Type:
        return self._api_client

    def execute(self) -> T_Return_Type:
        try:
            return self._execute_api_call()
        except ApiException as e:
            raise ExalsiusAPICommandError(
                message=f"An API error occurred: {str(e)}",
                status=e.status,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                reason=e.reason,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            ) from e
        except Exception as e:
            raise ExalsiusAPICommandError(
                message=f"An unexpected error occurred: {str(e)}",
            ) from e

    @abstractmethod
    def _execute_api_call(self) -> T_Return_Type:
        """Subclasses must implement this method to perform the actual API call."""
        pass

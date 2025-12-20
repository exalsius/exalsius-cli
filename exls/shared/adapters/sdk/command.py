from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from exalsius_api_client.exceptions import ApiException

from exls.shared.core.ports.command import BaseCommand, CommandError

T_API = TypeVar("T_API")
T_Cmd_Return = TypeVar("T_Cmd_Return")


class ExalsiusSdkCommandError(CommandError):
    def __init__(
        self,
        message: str,
        sdk_command: str,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        details: Optional[str] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.sdk_command: str = sdk_command
        self.status: Optional[int] = status
        self.reason: Optional[str] = reason
        self.details: Optional[str] = details
        self.retryable: bool = retryable

    def __str__(self):
        return (
            f"{self.message}\n"
            f"Error Status: {self.status if self.status else 'N/A'}\n"
            f"Error Details: {self.details if self.details else 'N/A'}"
        )


class UnexpectedSdkCommandResponseError(ExalsiusSdkCommandError):
    def __init__(
        self,
        message: str,
        sdk_command: str,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        details: Optional[str] = None,
        retryable: bool = True,
    ):
        super().__init__(message, sdk_command, status, reason, details, retryable)


class ExalsiusSdkCommand(
    BaseCommand[T_Cmd_Return],
    Generic[T_API, T_Cmd_Return],
    ABC,
):
    def __init__(self, api_client: T_API):
        self._api_client: T_API = api_client

    @property
    def api_client(self) -> T_API:
        return self._api_client

    def execute(self) -> T_Cmd_Return:
        try:
            return self._execute_api_call()
        except UnexpectedSdkCommandResponseError as e:
            raise ExalsiusSdkCommandError(
                message=f"The API returned an unexpected response: {e.message}",
                sdk_command=self.__class__.__name__,
                status=e.status,
                reason=e.reason,
                retryable=e.retryable,
                details=e.details,
            ) from e
        except ApiException as e:
            raise ExalsiusSdkCommandError(
                message=f"An API error occurred while executing the command {self.__class__.__name__}",
                sdk_command=self.__class__.__name__,
                retryable=False,
                status=e.status,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                reason=e.reason,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                details=e.body,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            ) from e
        except Exception as e:
            raise ExalsiusSdkCommandError(
                message=f"An unexpected error occurred: {str(e)}",
                sdk_command=self.__class__.__name__,
            ) from e

    @abstractmethod
    def _execute_api_call(self) -> T_Cmd_Return:
        """Subclasses must implement this method to perform the actual API call."""
        pass

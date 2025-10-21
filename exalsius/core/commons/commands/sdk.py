from __future__ import annotations

from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from exalsius_api_client.exceptions import ApiException, ServiceException

from exalsius.core.base.commands import BaseCommand, CommandError

T_API = TypeVar("T_API")
T_Cmd_Return = TypeVar("T_Cmd_Return")
T_Cmd_Params = TypeVar("T_Cmd_Params")


class ExalsiusSdkCommandError(CommandError):
    def __init__(
        self,
        message: str,
        sdk_command: str,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.sdk_command: str = sdk_command
        self.status: Optional[int] = status
        self.reason: Optional[str] = reason
        self.retryable: bool = retryable

    def __str__(self):
        return f"ExalsiusSdkCommandError for {self.sdk_command}: {self.message} - Status: {self.status} - Reason: {self.reason}"


class UnexpectedSdkCommandResponseError(ExalsiusSdkCommandError):
    def __init__(
        self,
        message: str,
        sdk_command: str,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        retryable: bool = True,
    ):
        super().__init__(message, sdk_command, status, reason, retryable)


class ExalsiusSdkCommand(
    BaseCommand[T_Cmd_Return], Generic[T_API, T_Cmd_Params, T_Cmd_Return]
):
    def __init__(self, api_client: T_API, params: Optional[T_Cmd_Params]):
        self._api_client: T_API = api_client
        self._params: Optional[T_Cmd_Params] = params

    @property
    def api_client(self) -> T_API:
        return self._api_client

    @property
    def params(self) -> Optional[T_Cmd_Params]:
        return self._params

    def execute(self) -> T_Cmd_Return:
        try:
            return self._execute_api_call(self._params)
        # TODO: Retry logic should be placed in this class with respective configs etc.
        except UnexpectedSdkCommandResponseError as e:
            raise e
        except ServiceException as e:
            raise ExalsiusSdkCommandError(
                message=f"An API error occurred: {str(e)}",
                sdk_command=self.__class__.__name__,
                retryable=True,
                status=e.status,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                reason=e.reason,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            ) from e
        except ApiException as e:
            raise ExalsiusSdkCommandError(
                message=f"An API error occurred: {str(e)}",
                sdk_command=self.__class__.__name__,
                retryable=False,
                status=e.status,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                reason=e.reason,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            ) from e
        except Exception as e:
            raise ExalsiusSdkCommandError(
                message=f"An unexpected error occurred: {str(e)}",
                sdk_command=self.__class__.__name__,
            ) from e

    @abstractmethod
    def _execute_api_call(self, params: Optional[T_Cmd_Params]) -> T_Cmd_Return:
        """Subclasses must implement this method to perform the actual API call."""
        pass

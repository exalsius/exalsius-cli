from functools import wraps
from typing import Any, Callable, Type

from exls.shared.adapters.ui.display.display import UserCancellationException
from exls.shared.core.domain import ExalsiusError
from exls.shared.core.ports.command import CommandError
from exls.shared.core.service import ServiceError, ServiceWarning


def handle_service_errors(operation_name: str) -> Callable[..., Any]:
    """
    A decorator to handle common service layer errors.

    It catches CommandError, ServiceError and generic Exceptions and re-raises them
    as a consistent ServiceError.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ServiceWarning as e:
                raise e
            except ServiceError as e:
                raise e
            except CommandError as e:
                raise ServiceError(
                    message=f"error {operation_name}: {str(e)}",
                ) from e
            except Exception as e:
                # We catch the generic exception to ensure we always
                # return a ServiceError from the service layer.
                raise ServiceError(
                    message=f"unexpected error while {operation_name}: {str(e)}",
                ) from e

        return wrapper

    return decorator


def handle_interactive_flow_errors(
    operation_name: str, to_exception: Type[UserCancellationException]
) -> Callable[..., Any]:
    """
    A decorator to handle common interactive flow errors.

    It catches UserCancellationException and generic Exceptions and re-raises them
    as a consistent to_exception exception.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except UserCancellationException as e:
                raise to_exception(e) from e
            except Exception as e:
                # Any exception apart from UserCancellationException is unexpected and should be wrapped.
                raise ExalsiusError(
                    f"An unexpected error occurred during {operation_name}: {str(e)}"
                ) from e

        return wrapper

    return decorator

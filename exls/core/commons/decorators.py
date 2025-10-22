from functools import wraps
from typing import Any, Callable

from exls.core.base.commands import CommandError
from exls.core.base.service import ServiceError, ServiceWarning


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
                    message=f"error {operation_name}: {e.message}",
                ) from e
            except Exception as e:
                # We catch the generic exception to ensure we always
                # return a ServiceError from the service layer.
                raise ServiceError(
                    message=f"unexpected error while {operation_name}: {e}",
                ) from e

        return wrapper

    return decorator

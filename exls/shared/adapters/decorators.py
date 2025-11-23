from functools import wraps
from typing import Any, Callable, Type

import typer

from exls.shared.adapters.ui.display.display import UserCancellationException
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

        return wrapper

    return decorator


def handle_cli_errors(bundle_class: Type[Any]) -> Callable[..., Any]:
    """
    A decorator to handle ServiceError in CLI commands.

    It catches ServiceError, instantiates the bundle to get the display manager,
    displays the error message, and exits with code 1.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ServiceError as e:
                # Try to find ctx in args or kwargs
                ctx: typer.Context | None = None
                for arg in args:
                    if isinstance(arg, typer.Context):
                        ctx = arg
                        break
                if not ctx:
                    ctx = kwargs.get("ctx")

                if ctx:
                    bundle = bundle_class(ctx)
                    if hasattr(bundle, "get_interaction_manager"):
                        display_manager = bundle.get_interaction_manager()
                        display_manager.display_error_message(
                            str(e), output_format=bundle.message_output_format
                        )
                    else:
                        typer.echo(f"Error: {e}", err=True)
                else:
                    typer.echo(f"Error: {e}", err=True)

                raise typer.Exit(1)

        return wrapper

    return decorator

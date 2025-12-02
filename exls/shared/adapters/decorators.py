from functools import wraps
from typing import Any, Callable, Type

import typer

from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.core.domain import ExalsiusError, ExalsiusWarning
from exls.shared.core.ports.command import CommandError
from exls.shared.core.service import ServiceError, ServiceWarning


def handle_service_layer_errors(operation_name: str) -> Callable[..., Any]:
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


def handle_application_layer_errors(
    bundle_class: Type[BaseBundle],
) -> Callable[..., Any]:
    """
    A decorator to handle ServiceError in CLI commands.

    It catches ServiceError, instantiates the bundle to get the display manager,
    displays the error message, and exits with code 1.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            def _get_ctx(args: Any, kwargs: Any) -> typer.Context | None:
                for arg in args:
                    if isinstance(arg, typer.Context):
                        return arg
                for _, value in kwargs.items():
                    if isinstance(value, typer.Context):
                        return value
                return None

            def _display_error_message(ctx: typer.Context, e: ExalsiusError) -> None:
                bundle: BaseBundle = bundle_class(ctx)
                bundle.get_io_facade().display_error_message(
                    str(e), output_format=bundle.message_output_format
                )

            def _display_info_message(ctx: typer.Context, e: ExalsiusWarning) -> None:
                bundle: BaseBundle = bundle_class(ctx)
                bundle.get_io_facade().display_info_message(
                    str(e), output_format=bundle.message_output_format
                )

            try:
                return func(*args, **kwargs)

            except UserCancellationException as e:
                ctx: typer.Context | None = _get_ctx(args, kwargs)
                if ctx:
                    _display_info_message(ctx, e)
                else:
                    typer.echo(f"{e}")
                raise typer.Exit(0)

            except ServiceError as e:
                ctx = _get_ctx(args, kwargs)
                if ctx:
                    _display_error_message(ctx, e)
                else:
                    typer.echo(f"{e}", err=True)

                raise typer.Exit(1)
            except ValueError as e:
                ctx = _get_ctx(args, kwargs)
                if ctx:
                    _display_error_message(ctx, ExalsiusError(str(e)))
                else:
                    typer.echo(f"{e}", err=True)
                raise typer.Exit(1)
            except Exception as e:
                ctx = _get_ctx(args, kwargs)
                if ctx:
                    _display_error_message(ctx, ExalsiusError(str(e)))
                else:
                    typer.echo(f"{e}", err=True)
                raise typer.Exit(1)

        return wrapper

    return decorator

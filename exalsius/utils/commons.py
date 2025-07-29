import sys
from typing import cast

import typer

from exalsius.config import AppConfig
from exalsius.core.commons.models import UnauthorizedError
from exalsius.state import AppState


def help_if_no_subcommand(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def get_app_state_from_ctx(ctx: typer.Context) -> AppState:
    """
    Get the CLI state from the context.
    """
    return cast(AppState, ctx.obj)


def get_config_from_ctx(ctx: typer.Context) -> AppConfig:
    """
    Get the CLI config from the context.
    """
    return get_app_state_from_ctx(ctx).config


def get_access_token_from_ctx(ctx: typer.Context) -> str:
    """
    Get the access token from the context.
    """
    app_state: AppState = get_app_state_from_ctx(ctx)
    if not app_state.access_token:
        raise UnauthorizedError(
            "No access token found in context. Please log in again."
        )
    return app_state.access_token


def is_interactive() -> bool:
    """Check if running in interactive environment (e.g., not CI/CD)."""
    return sys.stdout.isatty()

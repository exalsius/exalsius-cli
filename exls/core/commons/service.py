"""
Collection of common service utilities.
"""

import re
from typing import cast

import typer
from coolname import generate_slug  # type: ignore

from exls.config import AppConfig
from exls.core.base.service import ServiceError
from exls.state import AppState


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
        raise ServiceError(
            message="No access token found in context. Please log in again."
        )
    return app_state.access_token


def generate_random_name(prefix: str = "exalsius", slug_length: int = 2) -> str:
    """Generate a random name."""
    return f"{prefix}-{generate_slug(slug_length)}"


def validate_kubernetes_name(name: str) -> str:
    """Validate that the name is a valid Kubernetes name."""
    if len(name) > 63:
        raise typer.BadParameter("Name must be 63 characters or less.")
    if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", name):
        raise typer.BadParameter(
            "Name must consist of lower case alphanumeric characters or '-', "
            "and must start and end with an alphanumeric character."
        )
    return name

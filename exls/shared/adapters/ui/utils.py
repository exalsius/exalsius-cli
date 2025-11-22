import webbrowser
from typing import Optional, cast

import typer

from exls.config import AppConfig
from exls.shared.adapters.ui.display.values import OutputFormat
from exls.shared.core.service import ServiceError
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


def get_message_output_format_from_ctx(ctx: typer.Context) -> Optional[OutputFormat]:
    """
    Get the message output format from the context.
    """
    app_state: AppState = get_app_state_from_ctx(ctx)
    if app_state.message_output_format:
        return app_state.message_output_format
    return None


def get_object_output_format_from_ctx(ctx: typer.Context) -> Optional[OutputFormat]:
    """
    Get the object output format from the context.
    """
    app_state: AppState = get_app_state_from_ctx(ctx)
    if app_state.object_output_format:
        return app_state.object_output_format
    return None


def open_url_in_browser(url: str) -> bool:
    """
    Open a URL in the user's default web browser.

    Args:
        url: The URL to open

    Returns:
        True if the URL was successfully opened, False otherwise
    """
    try:
        return webbrowser.open(url)
    except Exception:
        return False

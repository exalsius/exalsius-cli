from typing import cast

import typer

from exalsius.cli.state import AppState


def help_if_no_subcommand(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def get_app_state_from_ctx(ctx: typer.Context) -> AppState:
    """
    Get the CLI state from the context.
    """
    return cast(AppState, ctx.obj)

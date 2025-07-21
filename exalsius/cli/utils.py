from typing import cast

import typer

from exalsius.cli.state import CLIState


def help_if_no_subcommand(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def get_cli_state(ctx: typer.Context) -> CLIState:
    """
    Get the CLI state from the context.
    """
    return cast(CLIState, ctx.obj)

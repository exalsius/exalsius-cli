import logging
from typing import Optional

import typer

from exalsius import __version__, clusters
from exalsius import config as cli_config
from exalsius import nodes, offers, workspaces
from exalsius.auth.cli import login, logout
from exalsius.auth.service import Auth0Service
from exalsius.core.commons.models import ServiceError
from exalsius.logging import setup_logging
from exalsius.state import AppState
from exalsius.utils import commons as utils

NON_AUTH_COMMANDS = ["login", "logout"]


app = typer.Typer()

# We add the login and logout commands to the root app to
# use them without a subcommand.
app.command()(login)
app.command()(logout)


app.add_typer(
    offers.cli.app,
    name="offers",
    help="List and manage GPU offers from cloud providers",
)

app.add_typer(
    nodes.cli.app,
    name="nodes",
    help="Manage the node pool",
)

app.add_typer(
    clusters.cli.app,
    name="clusters",
    help="Manage clusters",
)

app.add_typer(
    workspaces.cli.app,
    name="workspaces",
    help="Manage workspaces",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def __root(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    ),
    log_file: Optional[str] = typer.Option(
        None,
        "--log-file",
        help="Redirect logs to a file.",
    ),
):
    """
    exalsius CLI - A tool for distributed training and infrastructure management
    """
    setup_logging(log_level, log_file)
    logging.debug(f"Set log level to {log_level}")

    config: cli_config.AppConfig = cli_config.load_config()
    logging.debug(f"Loaded config: {config}")

    utils.help_if_no_subcommand(ctx)

    access_token: Optional[str] = None
    if ctx.invoked_subcommand not in NON_AUTH_COMMANDS:
        auth_service = Auth0Service(config)
        try:
            access_token = auth_service.acquire_access_token()
        except ServiceError as e:
            typer.echo(f"Authentication failed: {e.message}")
            typer.echo("Please log in again. Login command:")
            typer.echo("")
            typer.echo("exls login")
            typer.echo("")
        if not access_token:
            typer.echo("You are not logged in. Please log in. Login command:")
            typer.echo("")
            typer.echo("exls login")
            typer.echo("")
            raise typer.Exit(1)

    # Each command is responsible for checking the session for none
    ctx.obj = AppState(config=config, access_token=access_token)
    logging.debug(f"Using config: {ctx.obj.config}")


if __name__ == "__main__":
    app()

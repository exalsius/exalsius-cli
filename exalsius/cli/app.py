import logging
from typing import Optional

import typer

from exalsius import __version__
from exalsius.cli import auth
from exalsius.cli import config as cli_config
from exalsius.cli.commands import (
    clusters,
    login,
    management,
    nodes,
    offers,
    workspaces,
)
from exalsius.cli.logging import setup_logging
from exalsius.cli.state import CLIState

app = typer.Typer(context_settings={"allow_interspersed_args": True})

app.add_typer(
    login.app,
    name="login",
    help="Login with your Exalsius credentials",
)


app.add_typer(
    offers.app,
    name="offers",
    help="List and manage GPU offers from cloud providers",
)

app.add_typer(
    nodes.app,
    name="nodes",
    help="Manage the node pool",
)

app.add_typer(
    clusters.app,
    name="clusters",
    help="Manage clusters",
)

app.add_typer(
    workspaces.app,
    name="workspaces",
    help="Manage workspaces",
)

app.add_typer(
    management.app,
    name="management",
    help="Manage SSH keys, cluster templates, and cloud credentials",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def _root(
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
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        help="The username to use for authentication.",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="The password to use for authentication.",
        callback=auth.username_password_together_callback,
    ),
):
    """
    exalsius CLI - A tool for distributed training and infrastructure management
    """
    setup_logging(log_level, log_file)
    logging.debug(f"Set log level to {log_level}")

    config = cli_config.load_config()
    logging.debug(f"Loaded config: {config}")

    # TODO: I dont like the whole authentication workflow
    #       It's like this because login does not need a session but all other commands do
    #       and typer does not support a grouping of commands by common arguments
    #       Dependency injection might be a way to go but I dont know yet how to do it
    try:
        session = auth.get_session(username, password)
    except auth.AuthenticationError as e:
        typer.echo(e)
        raise typer.Exit(1)

    # Each command is responsible for checking the session for none
    ctx.obj = CLIState(config=config, session=session)
    logging.debug(f"Using config: {ctx.obj.config}")


if __name__ == "__main__":
    app()

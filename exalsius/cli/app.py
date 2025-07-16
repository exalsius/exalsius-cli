import logging
from typing import Optional

import typer
from rich.console import Console

from exalsius import __version__
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
from exalsius.cli.state import BaseState
from exalsius.core.models.auth import (
    AuthRequest,
    Credentials,
    ValidateSessionRequest,
    load_credentials,
    load_session,
)
from exalsius.core.services.auth_service import AuthService, SessionService
from exalsius.display.auth_display import AuthDisplayManager
from exalsius.utils.theme import custom_theme

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


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"exalsius CLI version {__version__}")
        raise typer.Exit()


def together_callback(value: str, ctx: typer.Context) -> str | None:
    # ctx.params already contains values parsed for previously-declared params
    mate = ctx.params.get("password")
    if (value is None) ^ (mate is None):  # XOR: exactly one given -> error
        raise typer.BadParameter(
            "--user and --password must be supplied together (or omitted together)"
        )
    return value


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
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

    config = cli_config.load_config()
    logging.debug(f"Loaded config: {config}")

    auth_service = AuthService()

    console = Console(theme=custom_theme)
    auth_display = AuthDisplayManager(console)

    session = None
    if username and password:
        auth_request: AuthRequest = AuthRequest(
            credentials=Credentials(username=username, password=password)
        )
        auth_response, error = auth_service.authenticate(auth_request)
        if error:
            auth_display.print_error(f"Authentication failed: {error}")
            raise typer.Exit(1)
    else:
        session = load_session()
        if session:
            session_service = SessionService(session)
            validate_session_response, error = session_service.validate_session(
                ValidateSessionRequest(session=session)
            )
            if error:
                try:
                    credentials = load_credentials()
                except ValueError:
                    auth_display.print_error(
                        "Not credentials found. Please login via 'exls login' or "
                        "provide credentials with --username and --password"
                    )
                    raise typer.Exit(1)
                auth_request = AuthRequest(credentials=credentials)
                auth_response, error = auth_service.authenticate(auth_request)
                if error:
                    auth_display.print_error(f"Authentication failed: {error}")
                    raise typer.Exit(1)
        else:
            try:
                credentials = load_credentials()
            except ValueError:
                auth_display.print_error(
                    "Not credentials found. Please login via 'exls login' or "
                    "provide credentials with --username and --password"
                )
                raise typer.Exit(1)
            auth_request = AuthRequest(credentials=credentials)
            auth_response, error = auth_service.authenticate(auth_request)
            if error:
                auth_display.print_error(f"Authentication failed: {error}")
                raise typer.Exit(1)
            if auth_response:
                session = auth_response.session
            else:
                auth_display.print_error("Authentication failed")
                raise typer.Exit(1)

    ctx.obj = BaseState(config=config, session=session)
    logging.debug(f"Using config: {ctx.obj.config}")
    logging.debug(f"Using session: {ctx.obj.session}")

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()

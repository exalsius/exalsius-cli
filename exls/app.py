import logging
from typing import Optional

import typer

from exls import config as cli_config
from exls.auth.cli import login, logout
from exls.auth.dtos import AcquiredAccessTokenDTO
from exls.auth.service import Auth0Service, NotLoggedInWarning, get_auth_service
from exls.clusters.cli import clusters_app
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.display import SimpleTextDisplayManager
from exls.core.commons.service import help_if_no_subcommand
from exls.logging import setup_logging
from exls.management.cli import management_app
from exls.nodes.cli import nodes_app
from exls.offers.cli import offers_app
from exls.services.cli import services_app
from exls.state import AppState
from exls.workspaces.cli import workspaces_app

NON_AUTH_COMMANDS = ["login", "logout"]


app = typer.Typer()

# We add the login, logout, and request_node_agent_tokens commands to the root app to
# use them without a subcommand.
app.command()(login)
app.command()(logout)


app.add_typer(
    offers_app,
    name="offers",
    help="List and manage GPU offers from cloud providers",
)

app.add_typer(
    nodes_app,
    name="nodes",
    help="Manage the node pool",
)

app.add_typer(
    clusters_app,
    name="clusters",
    help="Manage clusters",
)

app.add_typer(
    workspaces_app,
    name="workspaces",
    help="Manage workspaces of a cluster",
)

app.add_typer(
    services_app,
    name="services",
    help="Manage services of a cluster",
)

app.add_typer(
    management_app,
    name="management",
    help="Manage management resources",
)


def _version_callback(value: bool) -> None:
    if value:
        # TODO: Replace with actual version
        typer.echo("0.2.0")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def __root(  # pyright: ignore[reportUnusedFunction]
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

    help_if_no_subcommand(ctx)

    if ctx.invoked_subcommand not in NON_AUTH_COMMANDS:
        auth_service: Auth0Service = get_auth_service(config)
        display_manager: SimpleTextDisplayManager = SimpleTextDisplayManager()
        try:
            acquired_access_token: AcquiredAccessTokenDTO = (
                auth_service.acquire_access_token()
            )
        except NotLoggedInWarning:
            display_manager.display_error(
                ErrorDisplayModel(message="You are not logged in. Please log in.")
            )
            raise typer.Exit(1)
        except ServiceError:
            display_manager.display_error(
                ErrorDisplayModel(
                    message="Failed to acquire access token. Please log in again."
                )
            )
            raise typer.Exit(1)

        # Each command is responsible for checking the session for none and acquiring a new access token if needed
        ctx.obj = AppState(
            config=config, access_token=acquired_access_token.access_token
        )
    else:
        ctx.obj = AppState(config=config, access_token=None)
    logging.debug(f"Using config: {ctx.obj.config}")


if __name__ == "__main__":
    app()

import logging
from typing import Optional

import typer

from exls import config as cli_config
from exls.auth.adapters.bundle import AuthBundle
from exls.auth.adapters.dtos import AcquiredAccessTokenDTO
from exls.auth.adapters.ui.display.display import AuthInteractionManager
from exls.auth.app import login, logout
from exls.auth.core.service import AuthService, NotLoggedInWarning
from exls.clusters.app import clusters_app
from exls.logging import setup_logging
from exls.management.app import management_app
from exls.nodes.app import nodes_app
from exls.offers.app import offers_app
from exls.services.app import services_app
from exls.shared.adapters.ui.display.values import OutputFormat
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.service import ServiceError
from exls.state import AppState
from exls.workspaces.app import workspaces_app

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
    format: Optional[OutputFormat] = typer.Option(
        None,
        "--format",
        help=f"Set the output format ({', '.join([f.value for f in OutputFormat])}).",
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
        auth_service: AuthService = AuthBundle(ctx).get_auth_service(config=config)
        interaction_manager: AuthInteractionManager = AuthBundle(
            ctx
        ).get_interaction_manager()
        try:
            auth_session = auth_service.acquire_access_token()
            acquired_access_token: AcquiredAccessTokenDTO = (
                AcquiredAccessTokenDTO.from_loaded_token(auth_session.token)
            )
        except NotLoggedInWarning:
            interaction_manager.display_info_message(
                "You are not logged in. Please log in.",
                output_format=format or OutputFormat.TEXT,
            )
            raise typer.Exit(1)
        except ServiceError as e:
            interaction_manager.display_info_message(
                f"Failed to acquire access token. Please log in again. Error: {str(e)}",
                output_format=format or OutputFormat.TEXT,
            )
            raise typer.Exit(1)

        # Each command is responsible for checking the session for none and acquiring a new access token if needed
        ctx.obj = AppState(
            config=config,
            access_token=acquired_access_token.access_token,
            message_output_format=format,
            object_output_format=format,
        )
    else:
        ctx.obj = AppState(
            config=config,
            access_token=None,
            message_output_format=format,
            object_output_format=format,
        )
    logging.debug(f"Using config: {ctx.obj.config}")


if __name__ == "__main__":
    app()

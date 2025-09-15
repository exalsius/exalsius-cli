import logging

import typer
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.core.commons.models import ServiceError
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme
from exalsius.workspaces.display import WorkspacesDisplayManager
from exalsius.workspaces.service import WorkspacesService

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()
workspaces_deploy_app = typer.Typer()

workspaces_app.add_typer(workspaces_deploy_app, name="deploy")


@workspaces_app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_app.command("list")
def list_workspaces(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspaces_response = service.list_workspaces(cluster_id=cluster_id)

    if not workspaces_response:
        display_manager.print_warning("No workspaces found")
        return

    display_manager.display_workspaces(cluster_id, workspaces_response)


@workspaces_app.command("get")
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspace = service.get_workspace(workspace_id)
    if not workspace:
        display_manager.print_error(f"Workspace with ID {workspace_id} not found")
        raise typer.Exit(1)
    display_manager.display_workspace(workspace)


@workspaces_app.command("delete")
def delete_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspace_delete_response = service.delete_workspace(workspace_id)
    if not workspace_delete_response:
        display_manager.print_error(f"Workspace with ID {workspace_id} not found")
        raise typer.Exit(1)
    display_manager.display_workspace_deleted(workspace_delete_response.workspace_id)


def poll_workspace_creation(
    console: Console,
    display_manager: WorkspacesDisplayManager,
    service: WorkspacesService,
    workspace_create_response: WorkspaceCreateResponse,
) -> Workspace:
    with console.status(
        "[bold custom]Creating workspace...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        try:
            workspace_response = service._poll_workspace_creation(
                workspace_id=workspace_create_response.workspace_id
            )
        except TimeoutError:
            display_manager.print_warning(
                f"Workspace {workspace_create_response.workspace_id} did not become active in time. "
                + "This might be normal for some workspace types. Please check the status manually "
                + f"with `exls workspaces get {workspace_create_response.workspace_id}`."
            )
            raise typer.Exit(1)
        except ServiceError as e:
            display_manager.print_error(str(e))
            raise typer.Exit(1)
        except Exception as e:
            display_manager.print_error(f"Unexpected error: {str(e)}")
            raise typer.Exit(1)

    return workspace_response.workspace


# This serves as a registry for the workspaces CLI commands making sure they are imported and registered with typer

from exalsius.workspaces.devpod import cli as devpod_cli  # noqa: F401, E402
from exalsius.workspaces.diloco import cli as diloco_cli  # noqa: F401, E402
from exalsius.workspaces.jupyter import cli as jupyter_cli  # noqa: F401, E402
from exalsius.workspaces.llminference import cli as llminference_cli  # noqa: F401, E402

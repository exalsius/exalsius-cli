import logging
from enum import Enum
from typing import List, Union

import typer
from exalsius_api_client.models.workspace import Workspace

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError, ServiceWarning
from exalsius.utils import commons as utils
from exalsius.workspaces.display import (
    JsonWorkspacesDisplayManager,
    TableWorkspacesDisplayManager,
)
from exalsius.workspaces.service import WorkspacesService

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()
workspaces_deploy_app = typer.Typer()

workspaces_app.add_typer(workspaces_deploy_app, name="deploy")


class DisplayFormat(str, Enum):
    table = "table"
    json = "json"


@workspaces_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_app.command("list", help="List all workspaces of a cluster")
def list_workspaces(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
    format: DisplayFormat = typer.Option(
        DisplayFormat.table,
        "-f",
        "--format",
        help="The format to display the workspaces in",
        case_sensitive=False,
    ),
):
    display_manager: Union[
        TableWorkspacesDisplayManager, JsonWorkspacesDisplayManager
    ] = (
        TableWorkspacesDisplayManager()
        if format == DisplayFormat.table
        else JsonWorkspacesDisplayManager()
    )

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    try:
        workspaces: List[Workspace] = service.list_workspaces(cluster_id=cluster_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
    display_manager.display_workspaces(workspaces)


@workspaces_app.command("get", help="Get a workspace of a cluster")
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
    format: DisplayFormat = typer.Option(
        DisplayFormat.table,
        "-f",
        "--format",
        help="The format to display the workspace in",
        case_sensitive=False,
    ),
):
    display_manager: Union[
        TableWorkspacesDisplayManager, JsonWorkspacesDisplayManager
    ] = (
        TableWorkspacesDisplayManager()
        if format == DisplayFormat.table
        else JsonWorkspacesDisplayManager()
    )

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    try:
        workspace: Workspace = service.get_workspace(workspace_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
    display_manager.display_workspace(workspace)


@workspaces_app.command("delete", help="Delete a workspace of a cluster")
def delete_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    display_manager: TableWorkspacesDisplayManager = TableWorkspacesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    try:
        deleted_workspace_id: str = service.delete_workspace(workspace_id=workspace_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
    display_manager.display_success(
        f"Workspace {deleted_workspace_id} deleted successfully."
    )


def poll_workspace_creation(
    workspace_id: str,
    service: WorkspacesService,
    display_manager: TableWorkspacesDisplayManager,
) -> Workspace:
    display_manager.spinner_display.start_display("Creating workspace...")
    try:
        workspace: Workspace = service.poll_workspace_creation(
            workspace_id=workspace_id
        )
    except TimeoutError as e:
        display_manager.display_info(
            f"workspace creation timed out: {e}. "
            + "Please check the status manually "
            + f"with `exls workspaces get {workspace_id}`."
        )
        raise typer.Exit(1)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
    except ServiceWarning as e:
        display_manager.display_info(str(e))
        raise typer.Exit(1)
    finally:
        display_manager.spinner_display.stop_display()

    return workspace


# isort: off
# This serves as a registry for the workspaces CLI commands making sure they are imported and registered with typer

from exalsius.workspaces.devpod import (  # noqa: F401, E402; pyright: ignore[reportUnusedImport]
    cli as devpod_cli,  # pyright: ignore[reportUnusedImport]
)
from exalsius.workspaces.diloco import (  # noqa: F401, E402; pyright: ignore[reportUnusedImport]
    cli as diloco_cli,  # pyright: ignore[reportUnusedImport]
)
from exalsius.workspaces.jupyter import (  # noqa: F401, E402; pyright: ignore[reportUnusedImport]
    cli as jupyter_cli,  # pyright: ignore[reportUnusedImport]
)
from exalsius.workspaces.llminference import (  # noqa: F401, E402; pyright: ignore[reportUnusedImport]
    cli as llminference_cli,  # pyright: ignore[reportUnusedImport]
)

# isort: on

import logging
from enum import StrEnum
from typing import List, Union

import typer

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.utils import commons as utils
from exalsius.workspaces.display import (
    JsonWorkspacesDisplayManager,
    TableWorkspacesDisplayManager,
)
from exalsius.workspaces.dtos import ListWorkspacesRequestDTO, WorkspaceDTO
from exalsius.workspaces.service import WorkspacesService, get_workspaces_service

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()
workspaces_deploy_app = typer.Typer()

workspaces_app.add_typer(workspaces_deploy_app, name="deploy")


class DisplayFormat(StrEnum):
    TABLE = "table"
    JSON = "json"


def _get_workspaces_service(ctx: typer.Context) -> WorkspacesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return get_workspaces_service(config, access_token)


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
        DisplayFormat.TABLE,
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
        if format == DisplayFormat.TABLE
        else JsonWorkspacesDisplayManager()
    )

    service = _get_workspaces_service(ctx)

    try:
        workspaces: List[WorkspaceDTO] = service.list_workspaces(
            ListWorkspacesRequestDTO(cluster_id=cluster_id)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
    display_manager.display_workspaces(workspaces)


@workspaces_app.command("get", help="Get a workspace of a cluster")
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
    format: DisplayFormat = typer.Option(
        DisplayFormat.TABLE,
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
        if format == DisplayFormat.TABLE
        else JsonWorkspacesDisplayManager()
    )

    service = _get_workspaces_service(ctx)

    try:
        workspace: WorkspaceDTO = service.get_workspace(workspace_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
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

    service = _get_workspaces_service(ctx)

    try:
        service.delete_workspace(workspace_id=workspace_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
    display_manager.display_success(f"Workspace {workspace_id} deleted successfully.")


def poll_workspace_creation(
    workspace_id: str,
    service: WorkspacesService,
    display_manager: TableWorkspacesDisplayManager,
) -> WorkspaceDTO:
    display_manager.spinner_display.start_display("Creating workspace...")
    try:
        workspace: WorkspaceDTO = service.poll_workspace_creation(
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
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
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
from exalsius.workspaces.marimo import (  # noqa: F401, E402; pyright: ignore[reportUnusedImport]
    cli as marimo_cli,  # pyright: ignore[reportUnusedImport]
)

# isort: on

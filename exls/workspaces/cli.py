import logging
from pathlib import Path
from typing import List, Optional

import typer

from exls.clusters.dtos import ClusterDTO, ListClustersRequestDTO
from exls.clusters.service import ClustersService, get_clusters_service
from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.exceptions import ExalsiusError
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)
from exls.management.types.workspace_templates.dtos import (
    ListWorkspaceTemplatesRequestDTO,
    WorkspaceTemplateDTO,
)
from exls.management.types.workspace_templates.service import (
    WorkspaceTemplatesService,
    get_workspace_templates_service,
)
from exls.workspaces.display import (
    BaseWorkspaceDisplayManager,
    ComposingWorkspaceDisplayManager,
    TableWorkspacesDisplayManager,
)
from exls.workspaces.dtos import (
    DeployWorkspaceRequestDTO,
    ListWorkspacesRequestDTO,
    WorkspaceDTO,
)
from exls.workspaces.interactive.flow import (
    WorkspaceFlowInterruptionException,
    WorkspaceInteractiveFlow,
)
from exls.workspaces.service import WorkspacesService, get_workspaces_service

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()


def _get_workspaces_service(ctx: typer.Context) -> WorkspacesService:
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    return get_workspaces_service(config, access_token)


@workspaces_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    help_if_no_subcommand(ctx)


@workspaces_app.command("list", help="List all workspaces of a cluster")
def list_workspaces(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
):
    display_manager: BaseWorkspaceDisplayManager = TableWorkspacesDisplayManager()

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
):
    display_manager: BaseWorkspaceDisplayManager = TableWorkspacesDisplayManager()

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
    display_manager: BaseWorkspaceDisplayManager = TableWorkspacesDisplayManager()

    service = _get_workspaces_service(ctx)

    try:
        service.delete_workspace(workspace_id=workspace_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
    display_manager.display_success(f"Workspace {workspace_id} deleted successfully.")


@workspaces_app.command("deploy", help="Deploy a workspace")
def deploy_workspace(
    ctx: typer.Context,
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to workspace deployment config YAML file. If not provided, runs in interactive mode.",
    ),
):
    """
    Deploy a workspace.

    When called without options, runs in interactive mode:
    - Guides through cluster selection, template selection, and configuration
    - Saves configuration to YAML file
    - Prompts for deployment confirmation

    When called with --config, deploys from configuration file:
    - Loads configuration from YAML file
    - Validates and deploys directly
    """
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    workspace_service: WorkspacesService = get_workspaces_service(config, access_token)
    clusters_service: ClustersService = get_clusters_service(config, access_token)
    workspace_templates_service: WorkspaceTemplatesService = (
        get_workspace_templates_service(config, access_token)
    )

    display_manager: BaseWorkspaceDisplayManager = TableWorkspacesDisplayManager()

    try:
        clusters: List[ClusterDTO] = clusters_service.list_clusters(
            ListClustersRequestDTO()
        )
        templates: List[WorkspaceTemplateDTO] = (
            workspace_templates_service.list_workspace_templates(
                ListWorkspaceTemplatesRequestDTO()
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    # Config file mode
    if config_file:
        # try:
        #     #

        #     # Load config from file
        #     deploy_config: WorkspaceDeployConfigDTO = WorkspaceDeployConfigDTO.from_file(config_file)
        #     display_manager.display_info(f"Loaded configuration from {config_file}")
        #     display_manager.display_deploy_config(deploy_config)

        #     # Confirm deployment
        #     if not display_manager.ask_confirm(
        #         "Deploy workspace with this configuration?", default=True
        #     ):
        #         display_manager.display_info("Deployment cancelled by user.")
        #         raise typer.Exit()

        # except Exception as e:
        #     display_manager.display_error(
        #         ErrorDisplayModel(message=f"Failed to load config file: {str(e)}")
        #     )
        #     raise typer.Exit(1)
        print("Config file mode not implemented yet")
        raise typer.Exit(0)
    else:
        display: ComposingWorkspaceDisplayManager = ComposingWorkspaceDisplayManager(
            display_manager=display_manager
        )

        interactive_flow: WorkspaceInteractiveFlow = WorkspaceInteractiveFlow(
            clusters=clusters,
            workspace_templates=templates,
            display_manager=display,
        )
        try:
            deploy_request: DeployWorkspaceRequestDTO = interactive_flow.run()
        except WorkspaceFlowInterruptionException as e:
            display_manager.display_info(str(e))
            raise typer.Exit(0)
        except ExalsiusError as e:
            display_manager.display_error(ErrorDisplayModel(message=str(e)))
            raise typer.Exit(1)

        # TODO: Store config to file

    try:
        workspace: WorkspaceDTO = workspace_service.deploy_workspace(
            request=deploy_request
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    # Deploy workspace
    display_manager.display_success(
        f"Started workspace deployment for workspace {workspace.workspace_name}!"
    )
    display_manager.display_success(
        f"You can check the status of the deployment with `exls workspaces get {workspace.workspace_id}`"
    )

    # TODO: Implement workspace creation polling


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

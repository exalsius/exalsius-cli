import logging
from enum import StrEnum
from pathlib import Path
from typing import List, Optional, Union

import typer

from exls.clusters.dtos import ClusterDTO, ListClustersRequestDTO
from exls.clusters.service import ClustersService, get_clusters_service
from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
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
from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.common.display import (
    ComposingWorkspaceDeployDisplayManager,
    JsonWorkspacesDisplayManager,
    TableWorkspacesDisplayManager,
)
from exls.workspaces.common.dtos import (
    ListWorkspacesRequestDTO,
    WorkspaceDTO,
)
from exls.workspaces.common.service import WorkspacesService, get_workspaces_service
from exls.workspaces.interactive.orchestrator_flow import (
    WorkspaceDeployOrchestratorFlow,
)

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()


class DisplayFormat(StrEnum):
    TABLE = "table"
    JSON = "json"


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
    table_display_manager = TableWorkspacesDisplayManager()
    display_manager = ComposingWorkspaceDeployDisplayManager(
        display_manager=table_display_manager
    )

    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    # Config file mode
    if config_file:
        try:
            # Load config from file
            deploy_config = WorkspaceDeployConfigDTO.from_file(config_file)
            display_manager.display_info(f"Loaded configuration from {config_file}")
            display_manager.display_deploy_config(deploy_config)

            # Confirm deployment
            if not display_manager.ask_confirm(
                "Deploy workspace with this configuration?", default=True
            ):
                display_manager.display_info("Deployment cancelled by user.")
                raise typer.Exit()

        except Exception as e:
            display_manager.display_error(
                ErrorDisplayModel(message=f"Failed to load config file: {str(e)}")
            )
            raise typer.Exit(1)
    else:
        # Interactive mode
        display_manager.display_info("🚀 Starting interactive workspace deployment...")

        # Pre-fetch clusters
        clusters_service: ClustersService = get_clusters_service(config, access_token)
        try:
            clusters: List[ClusterDTO] = clusters_service.list_clusters(
                ListClustersRequestDTO()
            )
        except ServiceError as e:
            display_manager.display_error(
                ErrorDisplayModel(message=f"Failed to load clusters: {str(e)}")
            )
            raise typer.Exit(1)

        # Pre-fetch workspace templates
        templates_service: WorkspaceTemplatesService = get_workspace_templates_service(
            config, access_token
        )
        try:
            templates: List[WorkspaceTemplateDTO] = (
                templates_service.list_workspace_templates(
                    ListWorkspaceTemplatesRequestDTO()
                )
            )
        except ServiceError as e:
            display_manager.display_error(
                ErrorDisplayModel(message=f"Failed to load templates: {str(e)}")
            )
            raise typer.Exit(1)

        # Validate data availability
        if not clusters:
            display_manager.display_error(
                ErrorDisplayModel(
                    message="No clusters available. Please deploy a cluster first using 'exls clusters deploy'."
                )
            )
            raise typer.Exit(1)

        if not templates:
            display_manager.display_error(
                ErrorDisplayModel(
                    message="No workspace templates available. Please contact support."
                )
            )
            raise typer.Exit(1)

        # Run orchestrator flow
        orchestrator = WorkspaceDeployOrchestratorFlow(
            clusters=clusters,
            templates=templates,
            display_manager=display_manager,
        )

        try:
            deploy_config: Optional[WorkspaceDeployConfigDTO] = orchestrator.run()
        except Exception as e:
            display_manager.display_error(
                ErrorDisplayModel(message=f"Interactive flow failed: {str(e)}")
            )
            raise typer.Exit(1)

        if not deploy_config:
            display_manager.display_info("Deployment cancelled by user.")
            raise typer.Exit()

        # Save config to file
        config_filename = f"exls-ws-{deploy_config.workspace_name}.yaml"
        try:
            deploy_config.to_file(config_filename)
            display_manager.display_success(
                f"✅ Configuration saved to {config_filename}"
            )
        except Exception as e:
            display_manager.display_error(
                ErrorDisplayModel(
                    message=f"Failed to save configuration file: {str(e)}"
                )
            )
            # Continue anyway - config is already in memory

        # Confirm deployment
        if not display_manager.ask_confirm(
            "Proceed with workspace deployment?", default=True
        ):
            display_manager.display_info(
                f"Deployment cancelled. Configuration saved to {config_filename}. "
                f"You can deploy later using: exls workspaces deploy --config {config_filename}"
            )
            raise typer.Exit()

    # Deploy workspace
    display_manager.display_info("\n🚀 Deploying workspace...")

    # Get workspace service
    workspace_service: WorkspacesService = _get_workspaces_service(ctx)

    try:
        workspace_id: str = workspace_service.deploy_workspace(deploy_config)
        display_manager.display_success(
            f"✅ Workspace deployment initiated! Workspace ID: {workspace_id}"
        )

        # Poll for workspace creation
        display_manager.display_info("\n⏳ Waiting for workspace to become ready...")
        workspace: WorkspaceDTO = poll_workspace_creation(
            workspace_id=workspace_id,
            service=workspace_service,
            display_manager=table_display_manager,
        )

        display_manager.display_success(
            f"🎉 Workspace '{workspace.workspace_name}' is now running!"
        )
        display_manager.display_workspace(workspace)

    except Exception as e:
        display_manager.display_error(
            ErrorDisplayModel(message=f"Deployment failed: {str(e)}")
        )
        raise typer.Exit(1)


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

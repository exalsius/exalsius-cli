import logging
from typing import List

import typer

from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.workspaces.adapters.bundle import WorkspacesBundle
from exls.workspaces.adapters.dtos import (
    WorkspaceDTO,
)
from exls.workspaces.adapters.ui.display.display import IOWorkspacesFacade
from exls.workspaces.adapters.ui.mapper import (
    workspace_dto_from_domain,
)
from exls.workspaces.core.domain import Workspace

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()


@workspaces_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    help_if_no_subcommand(ctx)


@workspaces_app.command("list", help="List all workspaces of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def list_workspaces(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    workspaces: List[Workspace] = service.list_workspaces(cluster_id=cluster_id)
    workspace_dtos: List[WorkspaceDTO] = [
        workspace_dto_from_domain(workspace) for workspace in workspaces
    ]

    io_facade.display_data(workspace_dtos, bundle.object_output_format)


@workspaces_app.command("get", help="Get a workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    workspace: Workspace = service.get_workspace(workspace_id)
    workspace_dto: WorkspaceDTO = workspace_dto_from_domain(workspace)

    io_facade.display_data(workspace_dto, bundle.object_output_format)


@workspaces_app.command("delete", help="Delete a workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def delete_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    service.delete_workspace(workspace_id=workspace_id)

    io_facade.display_success_message(
        f"Workspace {workspace_id} deleted successfully.", bundle.message_output_format
    )


# @workspaces_app.command("deploy", help="Deploy a workspace")
# def deploy_workspace(
#     ctx: typer.Context,
#     config_file: Optional[str] = typer.Option(
#         None,
#         "--config",
#         "-c",
#         help="Path to workspace deployment config YAML file. If not provided, runs in interactive mode.",
#     ),
# ):
#     """
#     Deploy a workspace.
#     """
#     bundle = WorkspacesBundle(ctx)
#     interaction_manager = bundle.get_interaction_manager()
#     service = bundle.get_workspaces_service()

#     try:
#         clusters: List[ClusterDTO] = clusters_service.list_clusters(
#             ListClustersRequestDTO()
#         )
#         templates: List[WorkspaceTemplateDTO] = (
#             workspace_templates_service.list_workspace_templates(
#                 ListWorkspaceTemplatesRequestDTO()
#             )
#         )
#     except ServiceError as e:
#         display_manager.display_error(ErrorDisplayModel(message=str(e)))
#         raise typer.Exit(1)

#     if config_file:
#         # TODO: Implement config file loading
#         print("Config file mode not implemented yet")
#         raise typer.Exit(0)
#     else:
#         display: ComposingWorkspaceDisplayManager = ComposingWorkspaceDisplayManager(
#             display_manager=display_manager
#         )

#         interactive_flow: WorkspaceInteractiveFlow = WorkspaceInteractiveFlow(
#             clusters=clusters,
#             workspace_templates=templates,
#             display_manager=display,
#         )
#         try:
#             deploy_request_dto: DeployWorkspaceRequestDTO = interactive_flow.run()
#         except WorkspaceFlowInterruptionException as e:
#             display_manager.display_info(str(e))
#             raise typer.Exit(0)
#         except ExalsiusError as e:
#             display_manager.display_error(ErrorDisplayModel(message=str(e)))
#             raise typer.Exit(1)

#     try:
#         # Map DTO to Core Request
#         deploy_request: DeployWorkspaceRequest = deploy_workspace_request_from_dto(
#             deploy_request_dto
#         )

#         workspace: Workspace = service.deploy_workspace(request=deploy_request)
#         workspace_dto: WorkspaceDTO = WorkspaceDTO.from_domain(workspace)
#     except ServiceError as e:
#         display_manager.display_error(ErrorDisplayModel(message=str(e)))
#         raise typer.Exit(1)

#     display_manager.display_success(
#         f"Started workspace deployment for workspace {workspace_dto.workspace_name}!"
#     )
#     display_manager.display_success(
#         f"You can check the status of the deployment with `exls workspaces get {workspace_dto.id}`"
#     )

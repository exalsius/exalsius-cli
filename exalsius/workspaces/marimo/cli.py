import logging
from typing import List, Optional

import typer
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_access_information import (
    WorkspaceAccessInformation,
)
from pydantic import PositiveInt

from exalsius.config import AppConfig
from exalsius.utils import commons as utils
from exalsius.workspaces.cli import (
    poll_workspace_creation,
    workspaces_deploy_app,
)
from exalsius.workspaces.display import TableWorkspacesDisplayManager
from exalsius.workspaces.marimo.models import MarimoWorkspaceVariablesDTO
from exalsius.workspaces.marimo.service import MarimoWorkspacesService
from exalsius.workspaces.models import (
    ResourcePoolDTO,
    WorkspaceAccessInformationDTO,
)

logger: logging.Logger = logging.getLogger("cli.workspaces.marimo")


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage Marimo workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_deploy_app.command("marimo", help="Deploy a Marimo workspace")
def deploy_marimo_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-marimo"),
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated. It must be a valid kubernetes-formatted name.",
        show_default=False,
        callback=utils.validate_kubernetes_name,
    ),
    docker_image: Optional[str] = typer.Option(
        None,
        "--docker-image",
        "-i",
        help="The docker image to use for the workspace",
        show_default=False,
    ),
    marimo_password: str = typer.Option(
        ...,
        "--marimo-password",
        "-p",
        help="The password for the Marimo Webinterface",
    ),
    gpu_count: PositiveInt = typer.Option(
        1,
        "--gpu-count",
        "-g",
        help="The number of GPUs to add to the workspace",
    ),
    cpu_cores: PositiveInt = typer.Option(
        16,
        "--cpu-cores",
        "-c",
        help="The number of CPU cores to add to the workspace",
    ),
    memory_gb: PositiveInt = typer.Option(
        32,
        "--memory-gb",
        "-m",
        help="The amount of memory in GB to add to the workspace",
    ),
    pvc_storage_gb: PositiveInt = typer.Option(
        50,
        "--pvc-storage-gb",
        "-s",
        help="The amount of PVC storage in GB to add to the workspace",
    ),
    ephemeral_storage_gb: PositiveInt = typer.Option(
        50,
        "--ephemeral-storage-gb",
        "-e",
        help="The amount of ephemeral storage in GB to add to the workspace",
    ),
):
    display_manager: TableWorkspacesDisplayManager = TableWorkspacesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: MarimoWorkspacesService = MarimoWorkspacesService(config, access_token)

    resources: ResourcePoolDTO = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=pvc_storage_gb,
    )

    workspace_id: str = service.create_marimo_workspace(
        cluster_id=cluster_id,
        name=name,
        resources=resources,
        variables=MarimoWorkspaceVariablesDTO(
            deployment_name=name,
            deployment_image=docker_image,
            token_password=marimo_password,
            ephemeral_storage_gb=ephemeral_storage_gb,
        ),
    )

    workspace: Workspace = poll_workspace_creation(
        display_manager=display_manager,
        service=service,
        workspace_id=workspace_id,
    )

    access_infos: Optional[List[WorkspaceAccessInformation]] = (
        workspace.access_information
    )
    if not access_infos or len(access_infos) == 0:
        display_manager.display_success(
            f"workspace {workspace.name} ({workspace_id}) created successfully"
        )
        raise typer.Exit(0)

    access_info_dtos: List[WorkspaceAccessInformationDTO] = []
    for access_info in access_infos:
        access_info_dtos.append(
            WorkspaceAccessInformationDTO(
                workspace_id=workspace_id,
                access_type=access_info.access_type,
                access_endpoint=f"{access_info.access_protocol.lower()}://{access_info.external_ip}:{access_info.port_number}",
            )
        )

    display_manager.display_success(
        f"workspace {workspace.name} ({workspace_id}) created successfully."
    )
    display_manager.display_info("Access information:")
    display_manager.display_workspace_access_info(access_info_dtos)

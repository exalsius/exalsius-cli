import logging
from typing import Optional

import typer
from pydantic import PositiveInt

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.utils import commons as utils
from exalsius.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exalsius.workspaces.display import TableWorkspacesDisplayManager
from exalsius.workspaces.dtos import WorkspaceDTO, WorkspaceResourcesRequestDTO
from exalsius.workspaces.jupyter.dtos import DeployJupyterWorkspaceRequestDTO
from exalsius.workspaces.jupyter.service import (
    JupyterWorkspacesService,
    get_jupyter_workspaces_service,
)

logger: logging.Logger = logging.getLogger("cli.workspaces.jupyter")


def get_jupyter_workspaces_service_from_ctx(
    ctx: typer.Context,
) -> JupyterWorkspacesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return get_jupyter_workspaces_service(config=config, access_token=access_token)


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage Jupyter workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_deploy_app.command("jupyter", help="Deploy a Jupyter workspace")
def deploy_jupyter_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-jupyter"),
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
    jupyter_password: str = typer.Option(
        ...,
        "--jupyter-password",
        "-p",
        help="The password for the Jupyter notebook",
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

    service: JupyterWorkspacesService = get_jupyter_workspaces_service_from_ctx(ctx)

    deploy_jupyter_workspace_request: DeployJupyterWorkspaceRequestDTO = (
        DeployJupyterWorkspaceRequestDTO(
            cluster_id=cluster_id,
            name=name,
            docker_image=docker_image,
            jupyter_password=jupyter_password,
            resources=WorkspaceResourcesRequestDTO(
                gpu_count=gpu_count,
                gpu_type=None,
                gpu_vendor=None,
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                pvc_storage_gb=pvc_storage_gb,
                ephemeral_storage_gb=ephemeral_storage_gb,
            ),
            to_be_deleted_at=None,
        )
    )

    try:
        workspace_id: str = service.deploy_jupyter_workspace(
            request_dto=deploy_jupyter_workspace_request,
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    workspace: WorkspaceDTO = poll_workspace_creation(
        display_manager=display_manager,
        service=service,
        workspace_id=workspace_id,
    )

    display_manager.display_success(
        f"workspace {workspace.workspace_name} ({workspace.workspace_id}) created successfully."
    )
    display_manager.display_workspace(workspace)

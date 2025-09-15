import logging

import typer
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from pydantic import PositiveInt
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme
from exalsius.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exalsius.workspaces.devpod.models import DevPodWorkspaceVariablesDTO
from exalsius.workspaces.devpod.service import DevPodWorkspacesService
from exalsius.workspaces.display import WorkspacesDisplayManager
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)

logger = logging.getLogger("cli.workspaces.devpod")


@workspaces_deploy_app.command("dev-pod")
def deploy_pod_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-dev-pod"),
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated. It must be a valid kubernetes-formatted name.",
        show_default=False,
        callback=utils.validate_kubernetes_name,
    ),
    docker_image: str = typer.Option(
        "nvcr.io/nvidia/pytorch:25.01-py3",
        "--docker-image",
        "-i",
        help="The docker image to use for the workspace",
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
    ephemeral_storage_gb: PositiveInt = typer.Option(
        50,
        "--ephemeral-storage-gb",
        "-e",
        help="The amount of ephemeral storage in GB to add to the workspace",
    ),
    pvc_storage_gb: PositiveInt = typer.Option(
        50,
        "--pvc-storage-gb",
        "-p",
        help="The amount of PVC storage in GB to add to the workspace",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = DevPodWorkspacesService(config, access_token)

    resources = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=pvc_storage_gb,
    )

    workspace_create_response: WorkspaceCreateResponse = (
        service.create_devpod_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            variables=DevPodWorkspaceVariablesDTO(
                deployment_name=name,
                deployment_image=docker_image,
                ephemeral_storage_gb=ephemeral_storage_gb,
            ),
        )
    )

    workspace: Workspace = poll_workspace_creation(
        console=console,
        display_manager=display_manager,
        service=service,
        workspace_create_response=workspace_create_response,
    )

    display_manager.display_workspace_created(workspace)
    display_manager.display_workspace_access_info(workspace)

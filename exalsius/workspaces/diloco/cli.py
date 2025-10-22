import logging
from pathlib import Path
from typing import Optional

import typer
from pydantic import PositiveInt

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.utils import commons as utils
from exalsius.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exalsius.workspaces.diloco.dtos import DeployDilocoWorkspaceRequestDTO
from exalsius.workspaces.diloco.service import (
    DilocoWorkspacesService,
    get_diloco_workspaces_service,
)
from exalsius.workspaces.display import TableWorkspacesDisplayManager
from exalsius.workspaces.dtos import WorkspaceDTO, WorkspaceResourcesRequestDTO

logger: logging.Logger = logging.getLogger("cli.workspaces.diloco")


DEFAULT_DILCO_CONFIG_FILE = Path(__file__).parent / "default_config.yml"


def get_diloco_workspaces_service_from_ctx(
    ctx: typer.Context,
) -> DilocoWorkspacesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return get_diloco_workspaces_service(config=config, access_token=access_token)


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage DiLoCo workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_deploy_app.command("diloco", help="Deploy a DiLoCo workspace")
def deploy_diloco_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        "exls-diloco",
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated.",
        show_default=False,
        callback=utils.validate_kubernetes_name,
    ),
    nodes: PositiveInt = typer.Option(
        1,
        "--nodes",
        help="The number of nodes that are used for training",
    ),
    gpu_count_per_node: PositiveInt = typer.Option(
        1,
        "--gpu-count-per-node",
        "-g",
        help="The number of GPUs per node",
    ),
    cpu_cores_per_node: PositiveInt = typer.Option(
        16,
        "--cpu-cores-per-node",
        "-c",
        help="The number of CPU cores to add to the workspace",
    ),
    memory_gb_per_node: PositiveInt = typer.Option(
        32,
        "--memory-gb-per-node",
        "-m",
        help="The amount of memory in GB to add to the workspace",
    ),
    ephemeral_storage_gb_per_node: Optional[PositiveInt] = typer.Option(
        None,
        "--ephemeral-storage-gb-per-node",
        "-e",
        help="The amount of ephemeral storage in GB to add to the workspace.",
        show_default=False,
    ),
    diloco_config_file: Path = typer.Option(
        DEFAULT_DILCO_CONFIG_FILE,
        "--diloco-config-file",
        "-c",
        help="Path to the DiLoCo trainer config file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    wandb_user_key: Optional[str] = typer.Option(
        None,
        "--wandb-user-key",
        "-k",
        envvar=["WANDB_API_KEY"],
        help="The user key of the WandB project",
    ),
    wandb_project_name: Optional[str] = typer.Option(
        None,
        "--wandb-project-name",
        "-p",
        help="The name of the WandB project",
    ),
    wandb_group: Optional[str] = typer.Option(
        None,
        "--wandb-group",
        "-g",
        help="The group of the WandB project",
    ),
    huggingface_token: Optional[str] = typer.Option(
        None,
        "--huggingface-token",
        "-t",
        envvar=["HUGGINGFACE_TOKEN", "HF_TOKEN"],
        help="The HuggingFace token to use",
    ),
):
    display_manager: TableWorkspacesDisplayManager = TableWorkspacesDisplayManager()

    service: DilocoWorkspacesService = get_diloco_workspaces_service_from_ctx(ctx)

    deploy_diloco_workspace_request: DeployDilocoWorkspaceRequestDTO = (
        DeployDilocoWorkspaceRequestDTO(
            cluster_id=cluster_id,
            name=name,
            resources=WorkspaceResourcesRequestDTO(
                gpu_count=gpu_count_per_node,
                gpu_type=None,
                gpu_vendor=None,
                cpu_cores=cpu_cores_per_node,
                memory_gb=memory_gb_per_node,
                pvc_storage_gb=1,  # not supported by diloco
                ephemeral_storage_gb=ephemeral_storage_gb_per_node,
            ),
            nodes=nodes,
            diloco_config_file=diloco_config_file,
            wandb_user_key=wandb_user_key,
            wandb_project_name=wandb_project_name,
            wandb_group=wandb_group,
            huggingface_token=huggingface_token,
            to_be_deleted_at=None,
        )
    )

    try:
        workspace_id: str = service.deploy_diloco_workspace(
            request_dto=deploy_diloco_workspace_request,
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

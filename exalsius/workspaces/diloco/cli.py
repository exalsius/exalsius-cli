import logging
from pathlib import Path
from typing import Any, Optional

import typer
import yaml
from pydantic import PositiveInt

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.utils import commons as utils
from exalsius.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exalsius.workspaces.diloco.service import DilocoWorkspacesService
from exalsius.workspaces.display import TableWorkspacesDisplayManager
from exalsius.workspaces.dtos import ResourcePoolDTO, WorkspaceDTO

logger: logging.Logger = logging.getLogger("cli.workspaces.diloco")


DEFAULT_DILCO_CONFIG_FILE = Path(__file__).parent / "default_config.yml"


def get_diloco_workspaces_service(ctx: typer.Context) -> DilocoWorkspacesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return DilocoWorkspacesService(config, access_token)


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
        "-n",
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
    ephemeral_storage_gb_per_node: PositiveInt = typer.Option(
        50,
        "--ephemeral-storage-gb-per-node",
        "-e",
        help="The amount of ephemeral storage in GB to add to the workspace",
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

    service: DilocoWorkspacesService = get_diloco_workspaces_service(ctx)

    with open(diloco_config_file, "r") as f:
        config_data: dict[str, Any] = yaml.safe_load(f)

    diloco_config_from_file: dict[str, Any] = config_data.get("diloco", {})

    cli_args: dict[str, Optional[str]] = {
        "wandbUserKey": wandb_user_key,
        "wandbProjectName": wandb_project_name,
        "wandbGroup": wandb_group,
        "huggingfaceToken": huggingface_token,
    }
    cli_args_provided: dict[str, Any] = {
        k: v for k, v in cli_args.items() if v is not None
    }
    if "wandbUserKey" in cli_args_provided:
        cli_args_provided["wandbLogging"] = True

    merged_config: dict[str, Any] = {**diloco_config_from_file, **cli_args_provided}

    resources: ResourcePoolDTO = ResourcePoolDTO(
        gpu_count=gpu_count_per_node,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores_per_node,
        memory_gb=memory_gb_per_node,
        storage_gb=1,  # diloco workspaces do not support PVC storage, this will be ignored
    )

    variables = {
        "deploymentName": name,
        "nodes": nodes,
        "ephemeralStorageGb": ephemeral_storage_gb_per_node,
        "diloco": merged_config,
    }

    try:
        workspace_id: str = service.create_diloco_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            variables=variables,
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
        f"workspace {workspace.name} ({workspace_id}) created successfully."
    )
    display_manager.display_workspace(workspace)

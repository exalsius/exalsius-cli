import logging
from pathlib import Path
from typing import Any

import typer
import yaml
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from pydantic import PositiveInt
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme
from exalsius.workspaces.cli import workspaces_deploy_app
from exalsius.workspaces.diloco.models import (
    DilocoTrainerVariablesDTO,
    DilocoWorkspaceVariablesDTO,
)
from exalsius.workspaces.diloco.service import DilocoWorkspacesService
from exalsius.workspaces.display import WorkspacesDisplayManager
from exalsius.workspaces.models import ResourcePoolDTO

logger = logging.getLogger("cli.workspaces")


DEFAULT_DILCO_CONFIG_FILE = Path(__file__).parent / "default_config.yml"


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_deploy_app.command("diloco")
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
    wandb_user_key: str = typer.Option(
        None,
        "--wandb-user-key",
        "-k",
        envvar=["WANDB_API_KEY"],
        help="The user key of the WandB project",
    ),
    wandb_project_name: str = typer.Option(
        utils.generate_random_name(prefix="exls-diloco-project"),
        "--wandb-project-name",
        "-p",
        help="The name of the WandB project",
    ),
    wandb_group: str = typer.Option(
        utils.generate_random_name(prefix="exls-diloco-group"),
        "--wandb-group",
        "-g",
        help="The group of the WandB project",
    ),
    huggingface_token: str = typer.Option(
        None,
        "--huggingface-token",
        "-t",
        envvar=["HUGGINGFACE_TOKEN", "HF_TOKEN"],
        help="The HuggingFace token to use",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = DilocoWorkspacesService(config, access_token)

    with open(diloco_config_file, "r") as f:
        config_data = yaml.safe_load(f)

    diloco_config_from_file = config_data.get("diloco", {})

    cli_args = {
        "wandb_user_key": wandb_user_key,
        "wandb_project_name": wandb_project_name,
        "wandb_group": wandb_group,
        "huggingface_token": huggingface_token,
    }
    cli_args_provided: dict[str, Any] = {
        k: v for k, v in cli_args.items() if v is not None
    }
    if "wandb_user_key" in cli_args_provided:
        cli_args_provided["wandb_logging"] = True

    merged_config = {**diloco_config_from_file, **cli_args_provided}

    diloco_trainer_variables = DilocoTrainerVariablesDTO.model_validate(merged_config)

    resources: ResourcePoolDTO = ResourcePoolDTO(
        gpu_count=gpu_count_per_node,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores_per_node,
        memory_gb=memory_gb_per_node,
        storage_gb=1,  # diloco workspaces do not support PVC storage, this will be ignored
    )

    workspace_create_response: WorkspaceCreateResponse = (
        service.create_diloco_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            variables=DilocoWorkspaceVariablesDTO(
                deployment_name=name,
                nodes=nodes,
                ephemeral_storage_gb=ephemeral_storage_gb_per_node,
                diloco=diloco_trainer_variables,
            ),
        )
    )

    display_manager.display_workspace_created_from_response(workspace_create_response)

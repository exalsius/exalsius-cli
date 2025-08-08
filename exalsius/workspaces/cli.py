import logging
import time
from typing import Annotated

import typer
from exalsius_api_client.models.workspace import Workspace
from pydantic import PositiveInt
from rich.console import Console

from exalsius.config import AppConfig, ConfigDefaultCluster
from exalsius.state import AppState
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme
from exalsius.workspaces.display import WorkspacesDisplayManager
from exalsius.workspaces.models import (
    ResourcePoolDTO,
    WorkspaceTemplates,
)
from exalsius.workspaces.service import WorkspacesService

logger = logging.getLogger("cli.workspaces")

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    cluster: Annotated[
        str | None,
        typer.Option("--cluster", "-c", help="Cluster to use."),
    ] = None,
):
    """
    Manage workspaces.
    """
    utils.help_if_no_subcommand(ctx)

    if cluster:
        state: AppState = utils.get_app_state_from_ctx(ctx)
        state.config.default_cluster = ConfigDefaultCluster(
            id=cluster,
            name=cluster,
        )


@app.command("list")
def list_workspaces(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspaces_response = service.list_workspaces(cluster_id=cluster_id)

    if not workspaces_response:
        display_manager.print_warning("No workspaces found")
        return

    display_manager.display_workspaces(workspaces_response)


@app.command("get")
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspace = service.get_workspace(workspace_id)
    if not workspace:
        display_manager.print_error(f"Workspace with ID {workspace_id} not found")
        raise typer.Exit(1)
    display_manager.display_workspace(workspace)


@app.command("add")
def add_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Argument(
        help="The name of the workspace to add",
    ),
    gpu_count: PositiveInt = typer.Option(
        1,
        "--gpu-count",
        "-g",
        help="The number of GPUs to add to the workspace",
    ),
    workspace_type: WorkspaceTemplates = typer.Option(
        WorkspaceTemplates.POD,
        "--type",
        "-t",
        help='The type of the workspace to add. Can be "pod", "jupyter", or "llm_inference". Default is "pod"',
    ),
    jupyter_password: str = typer.Option(
        None,
        "--jupyter-password",
        "-p",
        help="The password for the Jupyter notebook",
    ),
    huggingface_model: str = typer.Option(
        None,
        "--huggingface-model",
        "-m",
        help="The HuggingFace-hosted LLM model to use for the workspace",
    ),
    huggingface_token: str = typer.Option(
        None,
        "--huggingface-token",
        "-h",
        help="The authentication token for working with HuggingFace-hosted LLM models that require authentication",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    if not cluster_id:
        active_cluster = utils.get_config_from_ctx(ctx).default_cluster
        if not active_cluster:
            display_manager.print_error(
                "Cluster not set. Please define a cluster with --cluster <cluster_id> or "
                "set a default cluster with `exalsius clusters set-default <cluster_id>`"
            )
            raise typer.Exit(1)
        cluster_id = active_cluster.id

    with console.status(
        "[bold custom]Creating workspace...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        # TODO: We generally need to improve the user feedback on what exactly happened / is happening.
        # TODO: We also need to improve the error handling in general.

        if workspace_type == WorkspaceTemplates.LLM_INFERENCE:
            if not huggingface_model:
                display_manager.print_warning(
                    "Workspace type is LLM inference, but no HuggingFace model was provided. Using the default model defined in the workspace template."
                )
            if not huggingface_token:
                display_manager.print_warning(
                    "Workspace type is LLM inference, but no HuggingFace token was provided. This might be a problem if the model requires authentication."
                )

        workspace_create_response = service.create_workspace(
            cluster_id=cluster_id,
            name=name,
            workspace_type=workspace_type,
            resources=ResourcePoolDTO(
                gpu_count=gpu_count,
                gpu_type=None,
                cpu_cores=16,
                memory_gb=32,
                storage_gb=50,
            ),
            jupyter_password=jupyter_password,
            huggingface_model=huggingface_model,
            huggingface_token=huggingface_token,
        )
        if not workspace_create_response:
            display_manager.print_error("Workspace creation failed.")
            raise typer.Exit(1)

        # TODO: add a timeout to the service and commands
        timeout = 120  # 2 minutes
        polling_interval = 5  # 5 seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            workspace_response = service.get_workspace(
                workspace_create_response.workspace_id
            )
            if not workspace_response:
                display_manager.print_error("Workspace not found.")
                raise typer.Exit(1)

            workspace: Workspace = workspace_response.workspace
            if workspace.workspace_status == "RUNNING":
                # TODO: This handles backend-side edge case where the status is running but the access info is not available yet.
                time.sleep(polling_interval)
                workspace_response = service.get_workspace(
                    workspace_create_response.workspace_id
                )
                break

            if workspace.workspace_status == "FAILED":
                display_manager.print_error("Workspace creation failed.")
                raise typer.Exit(1)

            time.sleep(polling_interval)
        else:
            display_manager.print_error(
                "Workspace did not become active in time. This might be normal for some workspace types. Please check the status manually."
            )
            raise typer.Exit(1)

        display_manager.display_workspace_created(workspace)
        display_manager.display_workspace_access_info(workspace)


@app.command("show-access-info")
def show_workspace_access_info(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to show the access information",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspace_response = service.get_workspace(workspace_id)
    if not workspace_response:
        display_manager.print_error(f"Workspace with ID {workspace_id} not found")
        raise typer.Exit(1)
    workspace: Workspace = workspace_response.workspace
    display_manager.display_workspace_access_info(workspace)


@app.command("delete")
def delete_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    workspace_delete_response = service.delete_workspace(workspace_id)
    if not workspace_delete_response:
        display_manager.print_error(f"Workspace with ID {workspace_id} not found")
        raise typer.Exit(1)
    display_manager.display_workspace_deleted(workspace_delete_response.workspace_id)

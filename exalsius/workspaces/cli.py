import logging

import typer
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from pydantic import PositiveInt
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.core.commons.models import ServiceError
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme
from exalsius.workspaces.display import WorkspacesDisplayManager
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)
from exalsius.workspaces.service import WorkspacesService

logger = logging.getLogger("cli.workspaces")

app = typer.Typer()
app_deploy = typer.Typer()
app_jupyter = typer.Typer()
app_llm_inference = typer.Typer()

app.add_typer(app_deploy, name="deploy")


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    utils.help_if_no_subcommand(ctx)


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


def _poll_workspace_creation(
    console: Console,
    display_manager: WorkspacesDisplayManager,
    service: WorkspacesService,
    workspace_create_response: WorkspaceCreateResponse,
) -> Workspace:
    with console.status(
        "[bold custom]Creating workspace...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        try:
            workspace_response = service._poll_workspace_creation(
                workspace_id=workspace_create_response.workspace_id
            )
        except TimeoutError:
            display_manager.print_warning(
                f"Workspace {workspace_create_response.workspace_id} did not become active in time. "
                + "This might be normal for some workspace types. Please check the status manually "
                + f"with `exls workspaces get {workspace_create_response.workspace_id}`."
            )
            raise typer.Exit(1)
        except ServiceError as e:
            display_manager.print_error(str(e))
            raise typer.Exit(1)
        except Exception as e:
            display_manager.print_error(f"Unexpected error: {str(e)}")
            raise typer.Exit(1)

    return workspace_response.workspace


@app_deploy.command("dev-pod")
def deploy_pod_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-dev-pod"),
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated.",
        show_default=False,
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
    storage_gb: PositiveInt = typer.Option(
        50,
        "--storage-gb",
        "-s",
        help="The amount of storage in GB to add to the workspace",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    resources = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=storage_gb,
    )

    workspace_create_response: WorkspaceCreateResponse = service.create_pod_workspace(
        cluster_id=cluster_id,
        name=name,
        resources=resources,
    )

    workspace: Workspace = _poll_workspace_creation(
        console=console,
        display_manager=display_manager,
        service=service,
        workspace_create_response=workspace_create_response,
    )

    display_manager.display_workspace_created(workspace)
    display_manager.display_workspace_access_info(workspace)


@app_deploy.command("jupyter")
def deploy_jupyter_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-jupyter"),
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated.",
        show_default=False,
    ),
    jupyter_password: str = typer.Option(
        None,
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
    storage_gb: PositiveInt = typer.Option(
        50,
        "--storage-gb",
        "-s",
        help="The amount of storage in GB to add to the workspace",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    resources = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=storage_gb,
    )

    workspace_create_response: WorkspaceCreateResponse = (
        service.create_jupyter_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            jupyter_password=jupyter_password,
        )
    )

    workspace: Workspace = _poll_workspace_creation(
        console=console,
        display_manager=display_manager,
        service=service,
        workspace_create_response=workspace_create_response,
    )

    display_manager.display_workspace_created(workspace)
    display_manager.display_workspace_access_info(workspace)


@app_deploy.command("llm-inference")
def deploy_llm_inference_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-llm-inference"),
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated.",
        show_default=False,
    ),
    huggingface_model: str = typer.Option(
        None,
        "--huggingface-model",
        "-m",
        help="The HuggingFace model to use",
    ),
    huggingface_token: str = typer.Option(
        None,
        "--huggingface-token",
        "-t",
        help="The HuggingFace token to use",
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
    storage_gb: PositiveInt = typer.Option(
        50,
        "--storage-gb",
        "-s",
        help="The amount of storage in GB to add to the workspace",
    ),
):
    console = Console(theme=custom_theme)
    display_manager = WorkspacesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = WorkspacesService(config, access_token)

    resources = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb,
        storage_gb=storage_gb,
    )

    workspace_create_response: WorkspaceCreateResponse = (
        service.create_llm_inference_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            huggingface_model=huggingface_model,
            huggingface_token=huggingface_token,
        )
    )

    workspace: Workspace = _poll_workspace_creation(
        console=console,
        display_manager=display_manager,
        service=service,
        workspace_create_response=workspace_create_response,
    )

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

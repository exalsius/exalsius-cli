import time
from typing import Annotated

import typer
from exalsius_api_client.models.workspace import Workspace
from pydantic import PositiveInt
from rich.console import Console

from exalsius.cli import config
from exalsius.core.models.workspaces import WorkspaceType
from exalsius.core.services.workspaces_services import WorkspacesService
from exalsius.display.workspaces_display import WorkspacesDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    cluster: Annotated[
        str | None,
        typer.Option("--cluster", "-c", help="Override active cluster for this call."),
    ] = None,
):
    """Manage workspaces"""
    # Store the resolved active cluster in Typer's context so sub-commands can reuse it
    ctx.obj = {"active_cluster": config.active_cluster(cluster)}

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("list")
def list_workspaces(
    ctx: typer.Context,
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)

    active_cluster = ctx.obj["active_cluster"]
    if not active_cluster:
        display_manager.print_error(
            "Cluster not set. Please define a cluster with --cluster <cluster_id> or "
            "set a default cluster with `exalsius clusters set-default <cluster_id>`"
        )
        raise typer.Exit(1)

    workspaces_response, error = service.list_workspaces(cluster_id=active_cluster.id)
    if error:
        display_manager.print_error(f"Error: {error}")
        raise typer.Exit(1)

    if not workspaces_response:
        display_manager.print_warning("No workspaces found")
        return

    display_manager.display_workspaces(workspaces_response)


@app.command("get")
def get_workspace(
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)
    workspace, error = service.get_workspace(workspace_id)
    if error:
        display_manager.print_error(f"Error: {error}")
        raise typer.Exit(1)
    display_manager.display_workspace(workspace)


@app.command("add")
def add_workspace(
    ctx: typer.Context,
    name: str = typer.Argument(
        help="The name of the workspace to add",
    ),
    owner: str = typer.Option(
        "exalsius",
        "--owner",
        "-o",
        help="The owner of the workspace to add",
    ),
    gpu_count: PositiveInt = typer.Option(
        1,
        "--gpu-count",
        "-g",
        help="The number of GPUs to add to the workspace",
    ),
    workspace_type: WorkspaceType = typer.Option(
        WorkspaceType.POD,
        "--type",
        "-t",
        help='The type of the workspace to add. Can be "pod" or "jupyter". Default is "pod"',
    ),
    jupyter_password: str = typer.Option(
        None,
        "--jupyter-password",
        "-p",
        help="The password for the Jupyter notebook",
    ),
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)

    active_cluster = ctx.obj["active_cluster"]
    if not active_cluster:
        typer.echo("No default cluster found")
        raise typer.Exit(1)

    with console.status(
        "[bold custom]Creating workspace...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        workspace_create_response, error = service.create_workspace(
            cluster_id=active_cluster.id,
            name=name,
            gpu_count=gpu_count,
            owner=owner,
            workspace_type=workspace_type,
            jupyter_password=jupyter_password,
        )
        if error:
            display_manager.print_error(f"Error while creating workspace: {error}")
            raise typer.Exit(1)

        # TODO: add a timeout to the service and operation
        timeout = 120  # 2 minutes
        polling_interval = 5  # 5 seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            workspace_response, error = service.get_workspace(
                workspace_create_response.workspace_id
            )
            if error:
                display_manager.print_warning(
                    f"Error while reading workspace status: {error}"
                )
                raise typer.Exit(1)

            workspace: Workspace = workspace_response.workspace
            if workspace.workspace_status == "RUNNING":
                # TODO: This handles backend-side edge case where the status is running but the access info is not available yet.
                time.sleep(polling_interval)
                workspace_response, error = service.get_workspace(
                    workspace_create_response.workspace_id
                )
                if error:
                    display_manager.print_warning(
                        f"Error while reading workspace status: {error}"
                    )
                    raise typer.Exit(1)
                break

            if workspace.workspace_status == "FAILED":
                display_manager.print_error("Workspace creation failed.")
                raise typer.Exit(1)

            time.sleep(polling_interval)
        else:
            display_manager.print_error(
                "Workspace did not become active in time. Please check the status manually."
            )
            raise typer.Exit(1)

        display_manager.display_workspace_created(workspace)
        display_manager.display_workspace_access_info(workspace)


@app.command("show-access-info")
def show_workspace_access_info(
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to show the access information",
    ),
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)
    workspace_response, error = service.get_workspace(workspace_id)
    if error:
        display_manager.print_error(f"Error: {error}")
        raise typer.Exit(1)
    workspace: Workspace = workspace_response.workspace
    display_manager.display_workspace_access_info(workspace)


@app.command("delete")
def delete_workspace(
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)
    workspace_delete_response, error = service.delete_workspace(workspace_id)
    if error:
        display_manager.print_error(f"Error: {error}")
        raise typer.Exit(1)

    display_manager.display_workspace_deleted(workspace_delete_response.workspace_id)

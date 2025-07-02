import typer
from rich.console import Console

from exalsius.core.services.workspaces_services import WorkspacesService
from exalsius.display.workspaces_display import WorkspacesDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """Manage workspaces"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("list")
def list_workspaces(
    cluster_id: str = typer.Option(
        None,
        "--cluster-id",
        "-c",
        help="The ID of the cluster to list workspaces for",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
):
    console = Console(theme=custom_theme)
    service = WorkspacesService()
    display_manager = WorkspacesDisplayManager(console)
    workspaces, error = service.list_workspaces()
    if error:
        typer.echo(f"Error: {error}")
        raise typer.Exit(1)

    if not workspaces:
        display_manager.print_warning("No workspaces found")
        return

    display_manager.display_workspaces(workspaces, verbose)

    @app.command("get")
    def get_workspace(workspace_id: str):
        console = Console(theme=custom_theme)
        service = WorkspacesService()
        display_manager = WorkspacesDisplayManager(console)
        workspace, error = service.get_workspace(workspace_id)
        if error:
            display_manager.print_error(f"Error: {error}")
            raise typer.Exit(1)
        display_manager.display_workspace(workspace)

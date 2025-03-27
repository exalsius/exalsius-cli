import typer
from rich.console import Console

from exalsius.commands.clouds.operations import ListEnabledCloudsOperation
from exalsius.display.clouds_display import CloudDisplayManager
from exalsius.services.clouds_service import CloudService
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command("list")
def list_enabled_clouds():
    """
    Lists all available cloud providers along with their status.
    """
    console = Console(theme=custom_theme)
    service = CloudService()
    display_manager = CloudDisplayManager(console)

    try:
        with console.status(
            "[bold custom]Checking for enabled clouds...[/bold custom]",
            spinner="bouncingBall",
            spinner_style="custom",
        ):
            clouds = service.execute_operation(ListEnabledCloudsOperation())
        display_manager.display_cloud_list(clouds)
    except Exception as e:
        console.print(f"[red]Error listing clouds: {str(e)}[/red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    List and manage cloud providers
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

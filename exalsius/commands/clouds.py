import typer
from rich.console import Console
from rich.theme import Theme
from sky.client import sdk

app = typer.Typer()

custom_theme = Theme(
    {
        "custom": "#f46907",
    }
)


def _check_clouds():
    # this check needs to be run first to get the enabled clouds
    sdk.stream_and_get(
        sdk.check(clouds=["kubernetes", "aws", "gcp"], verbose=False),
        output_stream="/dev/null",
    )


def _list_enabled_clouds() -> list[str]:
    enabled_clouds = sdk.stream_and_get(sdk.enabled_clouds())
    if enabled_clouds == []:
        _check_clouds()
        enabled_clouds = sdk.stream_and_get(sdk.enabled_clouds())
    return [str(c) for c in enabled_clouds]


@app.command("list")
def list_clouds() -> list[str]:
    """List all available configured clouds"""
    console = Console(theme=custom_theme)
    with console.status(
        "[bold custom]Checking for enabled clouds...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        enabled_clouds = _list_enabled_clouds()
    console.print("Enabled clouds:", style="custom")
    for cloud in enabled_clouds:
        console.print(f"[green]    - {cloud}[/green]", style="custom")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    List and submit training jobs
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

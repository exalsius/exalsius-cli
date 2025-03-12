import typer

from exalsius import __version__
from exalsius.commands.clouds import app as clouds_app
from exalsius.commands.colony import app as colony_app
from exalsius.commands.jobs import app as jobs_app
from exalsius.commands.scan_prices import app as prices_app

app = typer.Typer()

app.add_typer(clouds_app, name="clouds", help="List available configured clouds")
app.add_typer(
    prices_app,
    name="scan-prices",
    help="Scan and search for GPU prices across cloud providers",
)
app.add_typer(jobs_app, name="jobs", help="List and create training jobs")
app.add_typer(colony_app, name="colonies", help="List and create exalsius colonies")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"exalsius CLI version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    ctx: typer.Context = typer.Context,
):
    """
    exalsius CLI - A tool for distributed training and infrastructure management
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()

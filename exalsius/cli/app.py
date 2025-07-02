import typer

from exalsius import __version__
from exalsius.cli.commands import clusters, management, nodes, offers, workspaces

app = typer.Typer()

app.add_typer(
    offers.app,
    name="offers",
    help="List and manage GPU offers from cloud providers",
)

app.add_typer(
    nodes.app,
    name="nodes",
    help="Manage the node pool",
)

app.add_typer(
    clusters.app,
    name="clusters",
    help="Manage clusters",
)

app.add_typer(
    workspaces.app,
    name="workspaces",
    help="Manage workspaces",
)

app.add_typer(
    management.app,
    name="management",
    help="Manage SSH keys, cluster templates, and cloud credentials",
)


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

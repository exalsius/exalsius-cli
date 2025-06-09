import typer
from rich.console import Console

from exalsius.core.models.enums import CloudProvider, NodeType
from exalsius.core.services.node_service import NodeService
from exalsius.display.nodes_display import NodeDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """Manage the node pool"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("list")
def list_nodes(
    node_type: NodeType = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
    provider: CloudProvider = typer.Option(
        None, "--provider", "-p", help="The provider of the node to list"
    ),
):
    """List all nodes in the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService()
    display_manager = NodeDisplayManager(console)
    nodes, error = service.list_nodes(node_type, provider)
    if error:
        display_manager.print_error(f"Failed to list nodes: {error}")
        raise typer.Exit(1)
    display_manager.display_nodes(nodes)

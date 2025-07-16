import typer
from rich.console import Console

from exalsius.core.models.enums import CloudProvider, NodeType
from exalsius.core.services.node_service import NodeService
from exalsius.display.nodes_display import NodesDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Manage the node pool"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("list")
def list_nodes(
    ctx: typer.Context,
    node_type: NodeType = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
    provider: CloudProvider = typer.Option(
        None, "--provider", "-p", help="The provider of the node to list"
    ),
):
    """List all nodes in the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService(ctx.obj.config)
    display_manager = NodesDisplayManager(console)
    nodes, error = service.list_nodes(node_type, provider)
    if error:
        display_manager.print_error(f"Failed to list nodes: {error}")
        raise typer.Exit(1)
    display_manager.display_nodes(nodes)


@app.command("get")
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService(ctx.obj.config)
    display_manager = NodesDisplayManager(console)
    node, error = service.get_node(node_id)
    if error:
        display_manager.print_error(f"Failed to get node: {error}")
        raise typer.Exit(1)
    if node:
        display_manager.display_node(node)
    else:
        display_manager.print_error(f"Node {node_id} not found")
        raise typer.Exit(1)


@app.command("delete")
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService(ctx.obj.config)
    display_manager = NodesDisplayManager(console)
    node_delete_response, error = service.delete_node(node_id)
    if error:
        display_manager.print_error(f"Failed to delete node: {error}")
        raise typer.Exit(1)
    display_manager.print_success(f"Node {node_id} deleted successfully")


@app.command("import-ssh")
def import_ssh(
    ctx: typer.Context,
    hostname: str = typer.Option(help="The hostname of the node to import"),
    endpoint: str = typer.Option(help="The endpoint of the node to import"),
    username: str = typer.Option(help="The username of the node to import"),
    ssh_key_id: str = typer.Option(help="The ID of the SSH key to import"),
):
    """Import a self-managed node into the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService(ctx.obj.config)
    display_manager = NodesDisplayManager(console)
    node_import_response, error = service.import_ssh(
        hostname, endpoint, username, ssh_key_id
    )
    if error:
        display_manager.print_error(f"Failed to import SSH key: {error}")
        raise typer.Exit(1)
    if not node_import_response:
        display_manager.print_error("Failed to import SSH key")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Nodes {node_import_response.node_ids} imported successfully"
    )


@app.command("import-offer")
def import_offer(
    ctx: typer.Context,
    hostname: str = typer.Option(help="The hostname of the node to import"),
    offer_id: str = typer.Argument(help="The ID of the offer to import"),
    amount: int = typer.Option(help="The amount of nodes to import"),
):
    """Import a node from an offer into the node pool"""
    console = Console(theme=custom_theme)
    service = NodeService(ctx.obj.config)
    display_manager = NodesDisplayManager(console)
    node_import_response, error = service.import_from_offer(hostname, offer_id, amount)
    if error:
        display_manager.print_error(f"Failed to import offer: {error}")
        raise typer.Exit(1)
    if not node_import_response:
        display_manager.print_error("Failed to import offer")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Nodes {node_import_response.node_ids} imported successfully"
    )

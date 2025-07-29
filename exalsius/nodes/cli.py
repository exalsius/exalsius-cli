from pathlib import Path

import typer
from rich.console import Console

from exalsius.clusters.models import CloudProvider
from exalsius.nodes.display import NodesDisplayManager
from exalsius.nodes.models import NodeType
from exalsius.nodes.service import NodeService
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage the node pool.
    """
    utils.help_if_no_subcommand(ctx)


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
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)
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
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)

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
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)
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
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)
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
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)
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


@app.command("list")
def list_ssh_keys(ctx: typer.Context):
    """List all SSH keys in the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)

    ssh_keys, error = service.list_ssh_keys()
    if error:
        display_manager.print_error(f"Failed to list SSH keys: {error}")
        raise typer.Exit(1)
    display_manager.display_ssh_keys(ssh_keys)


@app.command("add")
def add_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name for the SSH key"),
    key_path: Path = typer.Option(
        ..., "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Add a new SSH key to the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)

    ssh_key_create_response, error = service.add_ssh_key(name, key_path)
    if error:
        display_manager.print_error(f"Failed to add SSH key: {error}")
        raise typer.Exit(1)
    if not ssh_key_create_response:
        display_manager.print_error("Failed to add SSH key.")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Added SSH key '{ssh_key_create_response.ssh_key_id}' from {key_path}"
    )


@app.command("delete")
def delete_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = NodeService(access_token)

    delete_success, error = service.delete_ssh_key(name)
    if not delete_success and error:
        display_manager.print_error(f"Failed to delete SSH key: {error}")
        raise typer.Exit(1)

    display_manager.print_success(f"Deleted SSH key '{name}'")

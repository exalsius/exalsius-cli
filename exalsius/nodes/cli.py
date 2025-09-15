from pathlib import Path

import typer
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.nodes.display import NodesDisplayManager
from exalsius.nodes.models import CloudProvider, NodeType
from exalsius.nodes.service import NodeService
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

nodes_app = typer.Typer()


@nodes_app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage the node pool.
    """
    utils.help_if_no_subcommand(ctx)


@nodes_app.command("list")
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
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        nodes_response = service.list_nodes(node_type, provider)
    except Exception as e:
        display_manager.print_error(f"Failed to list nodes: {e}")
        raise typer.Exit(1)

    display_manager.display_nodes(nodes_response.nodes)


@nodes_app.command("get")
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool"""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node_response = service.get_node(node_id)
    except Exception as e:
        display_manager.print_error(f"Failed to get node: {e}")
        raise typer.Exit(1)

    display_manager.display_node(node_response)


@nodes_app.command("delete")
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool"""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        service.delete_node(node_id)
    except Exception as e:
        display_manager.print_error(f"Failed to delete node: {e}")
        raise typer.Exit(1)

    display_manager.print_success(f"Node {node_id} deleted successfully")


@nodes_app.command("import-ssh")
def import_ssh(
    ctx: typer.Context,
    hostname: str = typer.Option(
        help="The hostname of the node to import",
        default_factory=utils.generate_random_name,
    ),
    endpoint: str = typer.Option(help="The endpoint of the node to import"),
    username: str = typer.Option(help="The username of the node to import"),
    ssh_key_id: str = typer.Option(help="The ID of the SSH key to import"),
):
    """Import a self-managed node into the node pool"""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node_import_response = service.import_ssh(
            hostname, endpoint, username, ssh_key_id
        )
    except Exception as e:
        display_manager.print_error(f"Failed to import node from SSH: {e}")
        raise typer.Exit(1)

    display_manager.print_success(
        f"Nodes {node_import_response.node_ids} imported successfully"
    )


@nodes_app.command("import-offer")
def import_offer(
    ctx: typer.Context,
    offer_id: str = typer.Argument(help="The ID of the offer to import"),
    hostname: str = typer.Option(
        help="The hostname of the node to import",
        default_factory=utils.generate_random_name,
    ),
    amount: int = typer.Option(
        help="The amount of nodes to import",
        default=1,
    ),
):
    """Import a node from an offer into the node pool"""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node_import_response = service.import_from_offer(hostname, offer_id, amount)
    except Exception as e:
        display_manager.print_error(f"Failed to import node from offer: {e}")
        raise typer.Exit(1)

    display_manager.print_success(
        f"Nodes {node_import_response.node_ids} imported successfully"
    )


@nodes_app.command("list-ssh-keys")
def list_ssh_keys(ctx: typer.Context):
    """List all SSH keys in the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service = NodeService(config, access_token)

    try:
        ssh_keys_response = service.list_ssh_keys()
    except Exception as e:
        display_manager.print_error(f"Failed to list SSH keys: {e}")
        raise typer.Exit(1)

    display_manager.display_ssh_keys(ssh_keys_response.ssh_keys)


@nodes_app.command("add-ssh-key")
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
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service = NodeService(config, access_token)

    try:
        ssh_key_create_response = service.add_ssh_key(name, key_path)
    except Exception as e:
        display_manager.print_error(f"Failed to add SSH key: {e}")
        raise typer.Exit(1)

    display_manager.print_success(
        f"Added SSH key '{ssh_key_create_response.ssh_key_id}' from {key_path}"
    )


@nodes_app.command("delete-ssh-key")
def delete_ssh_key(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="ID of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = NodesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        service.delete_ssh_key(id)
    except Exception as e:
        display_manager.print_error(f"Failed to delete SSH key: {e}")
        raise typer.Exit(1)

    display_manager.print_success(f"Deleted SSH key '{id}'")

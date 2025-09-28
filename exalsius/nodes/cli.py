from typing import List

import typer
from exalsius_api_client.models.base_node import BaseNode

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.nodes.display import TableNodesDisplayManager
from exalsius.nodes.models import CloudProvider, NodeType
from exalsius.nodes.service import NodeService
from exalsius.utils import commons as utils

nodes_app = typer.Typer()


@nodes_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage the node pool.
    """
    utils.help_if_no_subcommand(ctx)


@nodes_app.command("list", help="List all nodes in the node pool.")
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
    display_manager = TableNodesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        nodes: List[BaseNode] = service.list_nodes(node_type, provider)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_code=e.error_code,
                error_type=e.error_type,
            )
        )
        raise typer.Exit(1)

    display_manager.display_nodes(nodes)


@nodes_app.command("get", help="Get a node in the node pool.")
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool."""
    display_manager = TableNodesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node: BaseNode = service.get_node(node_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_code=e.error_code,
                error_type=e.error_type,
            )
        )
        raise typer.Exit(1)

    display_manager.display_node(node)


@nodes_app.command("delete", help="Delete a node in the node pool.")
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool."""
    display_manager = TableNodesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        service.delete_node(node_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_code=e.error_code,
                error_type=e.error_type,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(f"Node {node_id} deleted successfully")


@nodes_app.command("import-ssh", help="Import a self-managed node into the node pool.")
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
    """Import a self-managed node into the node pool."""
    display_manager = TableNodesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node_id: str = service.import_ssh_node(hostname, endpoint, username, ssh_key_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_code=e.error_code,
                error_type=e.error_type,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(f"Node {node_id} imported successfully")


@nodes_app.command(
    "import-offer", help="Import a node from an offer into the node pool."
)
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
    """Import a node from an offer into the node pool."""
    display_manager = TableNodesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = NodeService(config, access_token)

    try:
        node_ids: List[str] = service.import_from_offer(hostname, offer_id, amount)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_code=e.error_code,
                error_type=e.error_type,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(f"Nodes {node_ids} imported successfully")

from typing import List, Optional

import typer

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.nodes.display import TableNodesDisplayManager
from exalsius.nodes.domain import CloudProvider
from exalsius.nodes.dtos import (
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    NodeTypeDTO,
)
from exalsius.nodes.service import NodeService, get_node_service
from exalsius.utils import commons as utils

nodes_app = typer.Typer()


def _get_node_service(ctx: typer.Context) -> NodeService:
    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    return get_node_service(config, access_token)


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
    node_type: Optional[NodeTypeDTO] = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
    provider: Optional[CloudProvider] = typer.Option(
        None, "--provider", "-p", help="The provider of the node to list"
    ),
):
    """List all nodes in the node pool"""
    display_manager = TableNodesDisplayManager()

    service: NodeService = _get_node_service(ctx)

    try:
        nodes: List[NodeDTO] = service.list_nodes(
            NodesListRequestDTO(node_type=node_type, provider=provider)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_nodes(nodes)


@nodes_app.command("get", help="Get a node in the node pool.")
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool."""
    display_manager = TableNodesDisplayManager()

    service: NodeService = _get_node_service(ctx)

    try:
        node: NodeDTO = service.get_node(node_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_node(node)


@nodes_app.command("delete", help="Delete a node in the node pool.")
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool."""
    display_manager = TableNodesDisplayManager()

    service: NodeService = _get_node_service(ctx)

    try:
        service.delete_node(node_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
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

    service: NodeService = _get_node_service(ctx)

    try:
        node: NodeDTO = service.import_ssh_node(
            NodesImportSSHRequestDTO(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_id=ssh_key_id,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Node {node.hostname} imported successfully")
    display_manager.display_node(node)


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

    service: NodeService = _get_node_service(ctx)

    try:
        nodes: List[NodeDTO] = service.import_from_offer(
            NodesImportFromOfferRequestDTO(
                hostname=hostname,
                offer_id=offer_id,
                amount=amount,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Nodes {nodes} imported successfully")
    display_manager.display_nodes(nodes)

from typing import List, Optional

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.exceptions import ExalsiusError
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    generate_random_name,
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)
from exls.management.types.ssh_keys.dtos import ListSshKeysRequestDTO, SshKeyDTO
from exls.management.types.ssh_keys.service import SshKeysService, get_ssh_keys_service
from exls.nodes.display import ComposingNodeDisplayManager, TableNodesDisplayManager
from exls.nodes.dtos import (
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    NodeTypesDTO,
)
from exls.nodes.interactive.ssh_flow import (
    NodeImportSshFlow,
    NodeImportSshFlowInterruptionException,
)
from exls.nodes.service import NodeService, get_node_service

nodes_app = typer.Typer()


def _get_node_service(ctx: typer.Context) -> NodeService:
    access_token: str = get_access_token_from_ctx(ctx)
    config: AppConfig = get_config_from_ctx(ctx)
    return get_node_service(config, access_token)


@nodes_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage the node pool.
    """
    help_if_no_subcommand(ctx)


@nodes_app.command("list", help="List all nodes in the node pool.")
def list_nodes(
    ctx: typer.Context,
    node_type: Optional[NodeTypesDTO] = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
):
    """List all nodes in the node pool"""
    display_manager = TableNodesDisplayManager()

    service: NodeService = _get_node_service(ctx)

    try:
        nodes: List[NodeDTO] = service.list_nodes(
            NodesListRequestDTO(node_type=node_type)
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
        default_factory=generate_random_name,
    ),
    endpoint: str = typer.Option(help="The endpoint of the node to import"),
    username: str = typer.Option(help="The username of the node to import"),
    ssh_key_id: str = typer.Option(help="The ID of the SSH key to import"),
):
    """Import a self-managed node into the node pool."""
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    node_service: NodeService = get_node_service(config, access_token)
    ssh_keys_service: SshKeysService = get_ssh_keys_service(config, access_token)

    display_manager = TableNodesDisplayManager()

    try:
        ssh_key: SshKeyDTO = ssh_keys_service.get_ssh_key(ssh_key_id)
        node: NodeDTO = node_service.import_ssh_node(
            NodesImportSSHRequestDTO(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_name=ssh_key.name,
                ssh_key_id=ssh_key.id,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Node {node.hostname} imported successfully")
    display_manager.display_node(node)


# TODO: This is an experimental feature for now, so we're not exposing it yet.
def import_offer(
    ctx: typer.Context,
    offer_id: str = typer.Argument(help="The ID of the offer to import"),
    hostname: str = typer.Option(
        help="The hostname of the node to import",
        default_factory=generate_random_name,
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

    display_manager.display_success(
        f"Successfully imported {len(nodes)} nodes from offer {offer_id}"
    )
    display_manager.display_nodes(nodes)


@nodes_app.command("import", help="Import nodes using interactive mode")
def import_nodes(ctx: typer.Context):
    """Import nodes using interactive mode."""
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    node_service: NodeService = get_node_service(config, access_token)
    ssh_keys_service: SshKeysService = get_ssh_keys_service(config, access_token)

    display_manager: TableNodesDisplayManager = TableNodesDisplayManager()
    composing_display_manager: ComposingNodeDisplayManager = (
        ComposingNodeDisplayManager(display_manager=display_manager)
    )

    try:
        ssh_keys: List[SshKeyDTO] = ssh_keys_service.list_ssh_keys(
            ListSshKeysRequestDTO()
        )
    except ServiceError as e:
        display_manager.display_error(
            ErrorDisplayModel(message=f"Failed to load SSH keys: {str(e)}")
        )
        raise typer.Exit(1)

    # Validate at least one import method is available
    # TODO: Ask to start ssh key import flow
    if not ssh_keys:
        display_manager.display_error(
            ErrorDisplayModel(
                message="No SSH keys or offers available. Please add an SSH key using 'exls management ssh-keys add' or wait for offers to become available."
            )
        )
        raise typer.Exit(1)

    # TODO: We support only SSH import for now, but we should support offer import in the future.

    try:
        flow: NodeImportSshFlow = NodeImportSshFlow(
            available_ssh_keys=ssh_keys, display_manager=composing_display_manager
        )
        import_requests: List[NodesImportSSHRequestDTO] = flow.run()
    except NodeImportSshFlowInterruptionException:
        # display_manager.display_info(str(e))
        raise typer.Exit(0)
    except ExalsiusError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    try:
        nodes: List[NodeDTO] = node_service.import_ssh_nodes(import_requests)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Successfully imported {len(nodes)} nodes")
    display_manager.display_nodes(nodes)

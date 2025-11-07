from typing import List, Optional, Union

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
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
from exls.nodes.interactive.orchestrator_flow import NodeImportOrchestratorFlow
from exls.nodes.service import NodeService, get_node_service
from exls.offers.dtos import OfferDTO, OffersListRequestDTO
from exls.offers.service import OffersService, get_offers_service

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

    display_manager.display_success(f"Nodes {nodes} imported successfully")
    display_manager.display_nodes(nodes)


@nodes_app.command("import", help="Import nodes using interactive mode")
def import_nodes(ctx: typer.Context):
    """Import nodes using interactive mode."""
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    node_service: NodeService = get_node_service(config, access_token)
    ssh_keys_service: SshKeysService = get_ssh_keys_service(config, access_token)
    offers_service: OffersService = get_offers_service(config, access_token)

    table_display_manager = TableNodesDisplayManager()
    display_manager = ComposingNodeDisplayManager(display_manager=table_display_manager)

    try:
        ssh_keys: List[SshKeyDTO] = ssh_keys_service.list_ssh_keys(
            ListSshKeysRequestDTO()
        )
    except ServiceError as e:
        display_manager.display_error(
            ErrorDisplayModel(message=f"Failed to load SSH keys: {str(e)}")
        )
        raise typer.Exit(1)

    try:
        offers: List[OfferDTO] = offers_service.list_offers(OffersListRequestDTO())
    except ServiceError as e:
        display_manager.display_error(
            ErrorDisplayModel(message=f"Failed to load offers: {str(e)}")
        )
        raise typer.Exit(1)

    # Validate at least one import method is available
    if not ssh_keys and not offers:
        display_manager.display_error(
            ErrorDisplayModel(
                message="No SSH keys or offers available. Please add an SSH key using 'exls management ssh-keys add' or wait for offers to become available."
            )
        )
        raise typer.Exit(1)

    orchestrator_flow = NodeImportOrchestratorFlow(
        ssh_keys=ssh_keys,
        offers=offers,
        display_manager=display_manager,
    )

    try:
        import_dtos: List[
            Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]
        ] = orchestrator_flow.run()
    except Exception as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    if not import_dtos:
        display_manager.display_info("No nodes were imported.")
        raise typer.Exit()

    imported_nodes: List[NodeDTO] = []
    for dto in import_dtos:
        try:
            if isinstance(dto, NodesImportSSHRequestDTO):
                node: NodeDTO = node_service.import_ssh_node(dto)
                imported_nodes.append(node)
                display_manager.display_success(
                    f"Node {node.hostname} (ID: {node.id}) imported successfully!"
                )
            else:  # NodesImportFromOfferRequestDTO
                nodes: List[NodeDTO] = node_service.import_from_offer(dto)
                imported_nodes.extend(nodes)
                if len(nodes) == 1:
                    display_manager.display_success(
                        f"Node {nodes[0].hostname} (ID: {nodes[0].id}) imported successfully!"
                    )
                else:
                    display_manager.display_success(
                        f"{len(nodes)} nodes imported successfully!"
                    )
                    for node in nodes:
                        display_manager.display_info(
                            f"  - {node.hostname} (ID: {node.id})"
                        )
        except ServiceError as e:
            display_manager.display_error(
                ErrorDisplayModel(message=f"Import failed: {str(e)}")
            )

    if imported_nodes:
        display_manager.display_success(
            f"\n✅ Import session completed! Total nodes imported: {len(imported_nodes)}"
        )
        display_manager.display_nodes(imported_nodes)
    else:
        display_manager.display_error(ErrorDisplayModel(message="All imports failed."))
        raise typer.Exit(1)

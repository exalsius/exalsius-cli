from typing import List, Optional

import typer

from exls.nodes.adapters.bundle import NodesBundle
from exls.nodes.adapters.dtos import (
    NodeDTO,
)
from exls.nodes.adapters.ui.display.display import NodesInteractionManager
from exls.nodes.adapters.ui.mappers import node_dto_from_domain
from exls.nodes.adapters.values import NodeTypesDTO
from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    NodesFilterCriteria,
)
from exls.nodes.core.service import NodesService
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.service import ServiceError

nodes_app = typer.Typer()


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

    bundle: NodesBundle = NodesBundle(ctx)
    display_manager: NodesInteractionManager = bundle.get_interaction_manager()
    service: NodesService = bundle.get_nodes_service()

    try:
        domain_nodes: List[BaseNode] = service.list_nodes(
            NodesFilterCriteria(
                node_type=node_type.value.upper() if node_type else None
            )
        )
        nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(nodes, output_format=bundle.object_output_format)


@nodes_app.command("get", help="Get a node in the node pool.")
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    display_manager: NodesInteractionManager = bundle.get_interaction_manager()
    service: NodesService = bundle.get_nodes_service()

    try:
        domain_node: BaseNode = service.get_node(node_id)
        node: NodeDTO = node_dto_from_domain(domain_node)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(node, output_format=bundle.object_output_format)


@nodes_app.command("delete", help="Delete a node in the node pool.")
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    display_manager: NodesInteractionManager = bundle.get_interaction_manager()
    service: NodesService = bundle.get_nodes_service()

    try:
        service.delete_node(node_id)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_success_message(
        f"Node {node_id} deleted successfully",
        output_format=bundle.message_output_format,
    )


# @nodes_app.command("import-ssh", help="Import a self-managed node into the node pool.")
# def import_selfmanaged_node(
#     ctx: typer.Context,
#     hostname: str = typer.Option(
#         help="The hostname of the node to import",
#         default_factory=generate_random_name,
#     ),
#     endpoint: str = typer.Option(help="The endpoint of the node to import"),
#     username: str = typer.Option(help="The username of the node to import"),
#     ssh_key_id: str = typer.Option(help="The ID of the SSH key to import"),
# ):
#     """Import a self-managed node into the node pool."""
#     bundle: NodesBundle = NodesBundle(ctx)
#     node_service: NodesService = bundle.get_nodes_service()
#     display_manager: INodesDisplayManager = bundle.get_interaction_manager()

#     try:
#         ssh_key: SshKeyDTO = ssh_keys_service.get_ssh_key(ssh_key_id)
#         domain_node: BaseNode = node_service.import_selfmanaged_node(
#             ImportSelfmanagedNodeRequest(
#                 hostname=hostname,
#                 endpoint=endpoint,
#                 username=username,
#                 ssh_key_id=ssh_key.id,
#             )
#         )
#         node: NodeDTO = node_dto_from_domain(domain_node)
#     except ServiceError as e:
#         display_manager.display_error_message(
#             ErrorDisplayModel(message=str(e)), output_format=factory.get_output_format()
#         )
#         raise typer.Exit(1)

#     display_manager.display_success_message(
#         f"Node {node.hostname} imported successfully",
#         output_format=factory.get_output_format(),
#     )
#     display_manager.display_data(node, output_format=factory.get_output_format())


# # TODO: This is an experimental feature for now, so we're not exposing it yet.
# def import_offer(
#     ctx: typer.Context,
#     offer_id: str = typer.Argument(help="The ID of the offer to import"),
#     hostname: str = typer.Option(
#         help="The hostname of the node to import",
#         default_factory=generate_random_name,
#     ),
#     amount: int = typer.Option(
#         help="The amount of nodes to import",
#         default=1,
#     ),
# ):
#     """Import a node from an offer into the node pool."""
#     factory = NodesCommandFactory(ctx)
#     display_manager: INodesDisplayManager = factory.get_display_manager()
#     service: NodesService = factory.get_nodes_service()

#     try:
#         domain_nodes: List[BaseNode] = service.import_from_offer(
#             ImportCloudNodeRequest(
#                 hostname=hostname,
#                 offer_id=offer_id,
#                 amount=amount,
#             )
#         )
#         nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]
#     except ServiceError as e:
#         display_manager.display_error_message(
#             ErrorDisplayModel(message=str(e)), output_format=factory.get_output_format()
#         )
#         raise typer.Exit(1)

#     display_manager.display_success_message(
#         f"Successfully imported {len(nodes)} nodes from offer {offer_id}",
#         output_format=factory.get_output_format(),
#     )
#     display_manager.display_data(nodes, output_format=factory.get_output_format())


# @nodes_app.command("import", help="Import nodes using interactive mode")
# def import_nodes(ctx: typer.Context):
#     """Import nodes using interactive mode."""
#     factory = NodesCommandFactory(ctx)
#     node_service: NodesService = factory.get_nodes_service()
#     ssh_keys_service: SshKeysService = factory.get_ssh_keys_service()

#     # For interactive mode, we typically want table-like or interactive display manager.
#     # But factory returns one based on format.
#     # The ComposingNodeDisplayManager wraps it.

#     display_manager: INodesDisplayManager = factory.get_display_manager()
#     composing_display_manager: ComposingNodeDisplayManager = (
#         ComposingNodeDisplayManager(display_manager=display_manager)
#     )

#     try:
#         ssh_keys: List[SshKeyDTO] = ssh_keys_service.list_ssh_keys(
#             ListSshKeysRequestDTO()
#         )
#     except ServiceError as e:
#         display_manager.display_error_message(
#             ErrorDisplayModel(message=f"Failed to load SSH keys: {str(e)}"),
#             output_format=factory.get_output_format(),
#         )
#         raise typer.Exit(1)

#     # Validate at least one import method is available
#     # TODO: Ask to start ssh key import flow
#     if not ssh_keys:
#         display_manager.display_error_message(
#             ErrorDisplayModel(
#                 message="No SSH keys or offers available. Please add an SSH key using 'exls management ssh-keys add' or wait for offers to become available."
#             ),
#             output_format=factory.get_output_format(),
#         )
#         raise typer.Exit(1)

#     # TODO: We support only SSH import for now, but we should support offer import in the future.

#     try:
#         flow: NodeImportSshFlow = NodeImportSshFlow(
#             available_ssh_keys=ssh_keys, display_manager=composing_display_manager
#         )
#         import_requests_dtos: List[ImportSelfmanagedNodeRequestDTO] = flow.run()
#     except NodeImportSshFlowInterruptionException:
#         # display_manager.display_info(str(e))
#         raise typer.Exit(0)
#     except ExalsiusError as e:
#         display_manager.display_error_message(
#             ErrorDisplayModel(message=str(e)), output_format=factory.get_output_format()
#         )
#         raise typer.Exit(1)

#     try:
#         domain_requests: List[ImportSelfmanagedNodeRequest] = [
#             ImportSelfmanagedNodeRequest(
#                 hostname=req.hostname,
#                 endpoint=req.endpoint,
#                 username=req.username,
#                 ssh_key_id=req.ssh_key_id,
#             )
#             for req in import_requests_dtos
#         ]
#         domain_nodes: List[BaseNode] = node_service.import_ssh_nodes(domain_requests)
#         nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]
#     except ServiceError as e:
#         display_manager.display_error_message(
#             ErrorDisplayModel(message=str(e)), output_format=factory.get_output_format()
#         )
#         raise typer.Exit(1)

#     display_manager.display_success_message(
#         f"Successfully imported {len(nodes)} nodes",
#         output_format=factory.get_output_format(),
#     )
#     display_manager.display_data(nodes, output_format=factory.get_output_format())

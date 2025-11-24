from pathlib import Path
from typing import List, Optional

import typer

from exls.management.adapters.bundel import ManagementBundle
from exls.management.adapters.dtos import SshKeyDTO
from exls.management.adapters.ui.mapper import ssh_key_dto_from_domain
from exls.management.core.domain import SshKey
from exls.management.core.service import ManagementService
from exls.nodes.adapters.bundle import NodesBundle
from exls.nodes.adapters.dtos import (
    ImportSelfmanagedNodeRequestDTO,
    NodeDTO,
)
from exls.nodes.adapters.ui.display.display import IONodesFacade
from exls.nodes.adapters.ui.flows.node_import import SelfmanagedNodeImportFlow
from exls.nodes.adapters.ui.mappers import node_dto_from_domain
from exls.nodes.adapters.values import NodeTypesDTO
from exls.nodes.core.domain import BaseNode, SelfManagedNode
from exls.nodes.core.ports.provider import NodeSshKey
from exls.nodes.core.requests import (
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
)
from exls.nodes.core.service import NodesService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.domain import generate_random_name
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
@handle_application_layer_errors(NodesBundle)
def list_nodes(
    ctx: typer.Context,
    node_type: Optional[NodeTypesDTO] = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
):
    """List all nodes in the node pool"""

    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    domain_nodes: List[BaseNode] = service.list_nodes(
        NodesFilterCriteria(node_type=node_type.value.upper() if node_type else None)
    )
    dtos_nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]

    io_facade.display_data(data=dtos_nodes, output_format=bundle.object_output_format)


@nodes_app.command("get", help="Get a node in the node pool.")
@handle_application_layer_errors(NodesBundle)
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to get"),
):
    """Get a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    domain_node: BaseNode = service.get_node(node_id)
    node_dto: NodeDTO = node_dto_from_domain(domain_node)

    io_facade.display_data(data=node_dto, output_format=bundle.object_output_format)


@nodes_app.command("delete", help="Delete a node in the node pool.")
@handle_application_layer_errors(NodesBundle)
def delete_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(help="The ID of the node to delete"),
):
    """Delete a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    deleted_node_id: str = service.delete_node(node_id)

    io_facade.display_success_message(
        f"Node {deleted_node_id} deleted successfully",
        output_format=bundle.message_output_format,
    )


@nodes_app.command("import-ssh", help="Import a self-managed node into the node pool.")
@handle_application_layer_errors(NodesBundle)
def import_selfmanaged_node(
    ctx: typer.Context,
    hostname: str = typer.Option(
        help="The hostname of the node to import",
        default_factory=generate_random_name,
    ),
    endpoint: str = typer.Option(help="The endpoint of the node to import"),
    username: str = typer.Option(help="The username of the node to import"),
    ssh_key_id: Optional[str] = typer.Option(help="The ID of the SSH key to import"),
    ssh_key_path: Optional[Path] = typer.Option(
        help="The path to the SSH key to import"
    ),
    ssh_key_name: Optional[str] = typer.Option(
        help="The name of the SSH key to import"
    ),
):
    """Import a self-managed node into the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    final_ssh_key_id: Optional[str] = ssh_key_id

    if not final_ssh_key_id and ssh_key_path and ssh_key_name:
        domain_ssh_key: NodeSshKey = service.add_ssh_key(
            name=ssh_key_name, key_path=ssh_key_path
        )
        final_ssh_key_id = domain_ssh_key.id

    if not final_ssh_key_id:
        io_facade.display_error_message(
            "No SSH key ID provided and no SSH key path or name provided",
            output_format=bundle.message_output_format,
        )
        raise typer.Exit(1)

    domain_nodes: List[SelfManagedNode] = service.import_selfmanaged_nodes(
        [
            ImportSelfmanagedNodeRequest(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_id=final_ssh_key_id,
            )
        ]
    )
    dtos_nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]

    io_facade.display_success_message(
        message=f"Nodes {', '.join([node.hostname for node in domain_nodes])} imported successfully",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(data=dtos_nodes, output_format=bundle.object_output_format)


@nodes_app.command("import", help="Import nodes using interactive mode")
@handle_application_layer_errors(NodesBundle)
def import_nodes(ctx: typer.Context):
    """Import nodes using interactive mode."""
    bundle: NodesBundle = NodesBundle(ctx)
    node_service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    management_bundle: ManagementBundle = ManagementBundle(ctx)
    management_service: ManagementService = management_bundle.get_management_service()

    try:
        domain_ssh_keys: List[SshKey] = management_service.list_ssh_keys()
        ssh_keys: List[SshKeyDTO] = [
            ssh_key_dto_from_domain(key) for key in domain_ssh_keys
        ]
    except ServiceError as e:
        io_facade.display_error_message(
            message=f"Failed to load SSH keys: {str(e)}",
            output_format=bundle.message_output_format,
        )
        raise typer.Exit(1)

    # Validate at least one import method is available
    # TODO: Ask to start ssh key import flow
    if not ssh_keys:
        io_facade.display_error_message(
            message="No SSH keys or offers available. Please add an SSH key using 'exls management ssh-keys add' or wait for offers to become available.",
            output_format=bundle.message_output_format,
        )
        raise typer.Exit(1)

    # TODO: We support only SSH import for now, but we should support offer import in the future.

    try:
        flow: SelfmanagedNodeImportFlow = SelfmanagedNodeImportFlow(
            io_facade=io_facade,
            available_ssh_keys=ssh_keys,
        )
        import_requests_dtos: List[ImportSelfmanagedNodeRequestDTO] = flow.run()
    except UserCancellationException as e:
        io_facade.display_info_message(
            message=str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    domain_requests: List[ImportSelfmanagedNodeRequest] = [
        ImportSelfmanagedNodeRequest(
            hostname=req.hostname,
            endpoint=req.endpoint,
            username=req.username,
            ssh_key_id=req.ssh_key_id,
        )
        for req in import_requests_dtos
    ]
    domain_nodes: List[BaseNode] = node_service.import_selfmanaged_nodes(
        domain_requests
    )
    nodes: List[NodeDTO] = [node_dto_from_domain(node) for node in domain_nodes]

    io_facade.display_success_message(
        f"Successfully imported {len(nodes)} nodes",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(nodes, output_format=bundle.object_output_format)

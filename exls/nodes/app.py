from pathlib import Path
from typing import List, Optional, Union

import typer

from exls.nodes.adapters.bundle import NodesBundle
from exls.nodes.adapters.dtos import (
    NodeDTO,
    NodeImportFailureDTO,
)
from exls.nodes.adapters.ui.display.display import IONodesFacade
from exls.nodes.adapters.ui.dtos import ImportSelfmanagedNodeRequestListDTO
from exls.nodes.adapters.ui.flows.node_import import (
    ImportSelfmanagedNodeRequestListFlow,
)
from exls.nodes.adapters.ui.mappers import (
    node_dto_from_domain,
    node_import_failure_dto_from_domain,
)
from exls.nodes.adapters.values import NodeTypesDTO
from exls.nodes.core.domain import (
    BaseNode,
    SelfManagedNodesImportResult,
)
from exls.nodes.core.requests import (
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
    SshKeySpecification,
)
from exls.nodes.core.service import NodesService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.flow.flow import FlowContext
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.domain import generate_random_name

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

    final_ssh_key: Optional[Union[str, SshKeySpecification]] = None
    if ssh_key_id:
        final_ssh_key = ssh_key_id
    elif ssh_key_path and ssh_key_name:
        final_ssh_key = SshKeySpecification(name=ssh_key_name, key_path=ssh_key_path)
    else:
        io_facade.display_error_message(
            "No SSH key provided. Please provide an SSH key ID or a name and path to a new SSH key.",
            output_format=bundle.message_output_format,
        )
        raise typer.Exit(1)

    result: SelfManagedNodesImportResult = service.import_selfmanaged_nodes(
        [
            ImportSelfmanagedNodeRequest(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key=final_ssh_key,
            )
        ]
    )

    _display_import_result(1, result, bundle, io_facade)


@nodes_app.command("import", help="Import nodes using interactive mode")
@handle_application_layer_errors(NodesBundle)
def import_nodes(ctx: typer.Context):
    """Import nodes using interactive mode."""
    bundle: NodesBundle = NodesBundle(ctx)
    node_service: NodesService = bundle.get_nodes_service()
    io_facade: IONodesFacade = bundle.get_io_facade()

    flow: ImportSelfmanagedNodeRequestListFlow = (
        bundle.get_import_selfmanaged_nodes_flow()
    )
    import_selfmanaged_node_request_list: ImportSelfmanagedNodeRequestListDTO = (
        ImportSelfmanagedNodeRequestListDTO()
    )
    flow.execute(import_selfmanaged_node_request_list, FlowContext(), io_facade)

    result: SelfManagedNodesImportResult = node_service.import_selfmanaged_nodes(
        import_selfmanaged_node_request_list.nodes
    )

    _display_import_result(
        len(import_selfmanaged_node_request_list.nodes), result, bundle, io_facade
    )


def _display_import_result(
    num_imports: int,
    result: SelfManagedNodesImportResult,
    bundle: NodesBundle,
    io_facade: IONodesFacade,
) -> None:
    """Display the result of importing nodes."""

    if result.is_success:
        dtos_nodes: List[NodeDTO] = [
            node_dto_from_domain(node) for node in result.nodes
        ]
        io_facade.display_success_message(
            f"Successfully imported {len(result.nodes)} nodes:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=dtos_nodes, output_format=bundle.object_output_format
        )

    else:
        dtos_failures: List[NodeImportFailureDTO] = [
            node_import_failure_dto_from_domain(failure) for failure in result.failures
        ]
        io_facade.display_error_message(
            f"Failed to import {len(result.failures)} / {num_imports} nodes",
            output_format=bundle.message_output_format,
        )
        io_facade.display_info_message(
            "Failed imports: ",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=dtos_failures,
            output_format=bundle.object_output_format,
        )
        if result.nodes:
            dtos_nodes = [node_dto_from_domain(node) for node in result.nodes]
            io_facade.display_info_message(
                "Successfully imported nodes: ",
                output_format=bundle.message_output_format,
            )
            io_facade.display_data(
                data=dtos_nodes,
                output_format=bundle.object_output_format,
            )

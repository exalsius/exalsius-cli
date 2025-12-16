from pathlib import Path
from typing import List, Optional, Union

import typer

from exls.nodes.adapters.bundle import NodesBundle
from exls.nodes.adapters.ui.display.render import (
    NODE_IMPORT_FAILURE_VIEW,
    NODE_LIST_VIEW,
)
from exls.nodes.adapters.ui.flows.node_import import (
    FlowSelfmanagedNodeSpecificationDTO,
    ImportSelfmanagedNodeFlow,
)
from exls.nodes.adapters.values import AllowedNodeTypes
from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
    NodesSshKeySpecification,
)
from exls.nodes.core.results import (
    ImportSelfmanagedNodesResult,
)
from exls.nodes.core.service import NodesService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
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
    node_type: Optional[AllowedNodeTypes] = typer.Option(
        None, "--node-type", "-t", help="The type of node to list"
    ),
):
    """List all nodes in the node pool"""

    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    domain_nodes: List[BaseNode] = service.list_nodes(
        NodesFilterCriteria(node_type=node_type.value.upper() if node_type else None)
    )

    io_facade.display_data(
        data=domain_nodes,
        output_format=bundle.object_output_format,
        view_context=NODE_LIST_VIEW,
    )


@nodes_app.command("get", help="Get a node in the node pool.")
@handle_application_layer_errors(NodesBundle)
def get_node(
    ctx: typer.Context,
    node_id: str = typer.Argument(..., help="The ID of the node to get"),
):
    """Get a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    node: BaseNode = service.get_node(node_id)

    io_facade.display_data(
        data=node,
        output_format=bundle.object_output_format,
        view_context=NODE_LIST_VIEW,
    )


@nodes_app.command("delete", help="Delete a node in the node pool.")
@handle_application_layer_errors(NodesBundle)
def delete_nodes(
    ctx: typer.Context,
    node_ids: List[str] = typer.Argument(..., help="The IDs of the nodes to delete"),
):
    """Delete a node in the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    deleted_node_ids_result = service.delete_nodes(node_ids)

    io_facade.display_success_message(
        f"Nodes {', '.join(deleted_node_ids_result.deleted_node_ids)} deleted successfully",
        output_format=bundle.message_output_format,
    )
    if deleted_node_ids_result.issues:
        io_facade.display_error_message(
            f"Failed to delete {len(deleted_node_ids_result.issues)} nodes",
            output_format=bundle.message_output_format,
        )
        # We could add a view for delete issues if needed


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
    ssh_key_id: Optional[str] = typer.Option(
        None,
        "--ssh-key-id",
        help="The ID of the SSH key to import",
    ),
    ssh_key_path: Optional[Path] = typer.Option(
        None,
        "--ssh-key-path",
        help="The path to the SSH key to import",
    ),
    ssh_key_name: Optional[str] = typer.Option(
        None,
        "--ssh-key-name",
        help="The name of the SSH key to import",
    ),
):
    """Import a self-managed node into the node pool."""
    bundle: NodesBundle = NodesBundle(ctx)
    service: NodesService = bundle.get_nodes_service()
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    final_ssh_key: Optional[Union[str, NodesSshKeySpecification]] = None
    if ssh_key_id and ssh_key_path and ssh_key_name:
        raise ValueError(
            "You can either provide an SSH key ID or a SSH key name and path to "
            "the private key file to import a new SSH key, but not all three"
        )
    if ssh_key_id:
        final_ssh_key = ssh_key_id
    elif ssh_key_path and ssh_key_name:
        final_ssh_key = NodesSshKeySpecification(
            name=ssh_key_name, key_path=ssh_key_path
        )
    else:
        raise ValueError(
            "No SSH key provided. Please provide an SSH key ID or a name and path to a new SSH key."
        )

    result: ImportSelfmanagedNodesResult = service.import_selfmanaged_nodes(
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
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    flow: ImportSelfmanagedNodeFlow = bundle.get_import_selfmanaged_node_flow()
    flow_request: FlowSelfmanagedNodeSpecificationDTO = (
        FlowSelfmanagedNodeSpecificationDTO()
    )
    flow.execute(flow_request, FlowContext(), io_facade)

    # Convert Flow DTO to Domain Request
    import_request: ImportSelfmanagedNodeRequest = flow_request.to_domain()

    result: ImportSelfmanagedNodesResult = node_service.import_selfmanaged_nodes(
        [import_request]
    )

    _display_import_result(1, result, bundle, io_facade)


def _display_import_result(
    num_imports: int,
    result: ImportSelfmanagedNodesResult,
    bundle: NodesBundle,
    io_facade: IOBaseModelFacade,
) -> None:
    """Display the result of importing nodes."""

    if result.is_success:
        io_facade.display_success_message(
            f"Successfully imported {len(result.imported_nodes)} nodes:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.imported_nodes,
            output_format=bundle.object_output_format,
            view_context=NODE_LIST_VIEW,
        )

    else:
        io_facade.display_error_message(
            f"Failed to import {len(result.issues)} / {num_imports} nodes",
            output_format=bundle.message_output_format,
        )
        io_facade.display_info_message(
            "Failed imports: ",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.issues,
            output_format=bundle.object_output_format,
            view_context=NODE_IMPORT_FAILURE_VIEW,
        )
        if result.imported_nodes:
            io_facade.display_info_message(
                "Successfully imported nodes: ",
                output_format=bundle.message_output_format,
            )
            io_facade.display_data(
                data=result.imported_nodes,
                output_format=bundle.object_output_format,
                view_context=NODE_LIST_VIEW,
            )

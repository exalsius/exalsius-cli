from functools import singledispatch

from exls.nodes.adapters.dtos import (
    CloudNodeDTO,
    NodeDTO,
    NodeImportFailureDTO,
    SelfManagedNodeDTO,
)
from exls.nodes.core.domain import BaseNode, CloudNode, SelfManagedNode
from exls.nodes.core.ports.gateway import SelfManagedNodeImportFailure


@singledispatch
def node_dto_from_domain(
    node: BaseNode,
) -> NodeDTO:
    """Helper function to convert a domain node to a DTO node."""
    raise ValueError(f"Unknown node type: {type(node)}")


@node_dto_from_domain.register(CloudNode)
def _(node: CloudNode) -> CloudNodeDTO:
    """Helper function to convert a cloud domain node to a DTO node."""
    return CloudNodeDTO(
        id=node.id,
        hostname=node.hostname,
        import_time=node.import_time,
        node_status=node.node_status,
        provider=node.provider,
        instance_type=node.instance_type,
        price_per_hour=node.price_per_hour,
    )


@node_dto_from_domain.register(SelfManagedNode)
def _(node: SelfManagedNode) -> SelfManagedNodeDTO:
    """Helper function to convert a self-managed domain node to a DTO node."""
    return SelfManagedNodeDTO(
        id=node.id,
        hostname=node.hostname,
        import_time=node.import_time,
        node_status=node.node_status,
        endpoint=node.endpoint,
    )


def node_import_failure_dto_from_domain(
    failure: SelfManagedNodeImportFailure,
) -> NodeImportFailureDTO:
    """Helper function to convert a domain node import failure to a DTO node import failure."""
    return NodeImportFailureDTO(
        hostname=failure.node.hostname,
        error_message=f"{failure.message}: {failure.error}",
    )

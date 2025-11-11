from __future__ import annotations

from enum import StrEnum
from functools import singledispatch
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.domain import (
    BaseNode,
    CloudNode,
    SelfManagedNode,
)


# singledispatch transforms a regular function into a generic function
# which can have multiple different implementations, and the one that
# gets called depends on the type of the first argument passed to it.
@singledispatch
def node_dto_from_domain(node: BaseNode) -> NodeDTO:
    """Helper function to convert a domain node to a DTO node."""
    raise ValueError(f"Unknown node type: {type(node)}")


@node_dto_from_domain.register(CloudNode)
def _(node: CloudNode) -> CloudNodeDTO:
    """Helper function to convert a cloud domain node to a DTO node."""
    return CloudNodeDTO.from_domain(node)


@node_dto_from_domain.register(SelfManagedNode)
def _(node: SelfManagedNode) -> SelfManagedNodeDTO:
    """Helper function to convert a self-managed domain node to a DTO node."""
    return SelfManagedNodeDTO.from_domain(node)


class NodeTypesDTO(StrEnum):
    CLOUD = "cloud"
    SELF_MANAGED = "self-managed"


class AllowedNodeStatusFiltersDTO(StrEnum):
    AVAILABLE = "available"
    ADDED = "added"
    FAILED = "failed"


class NodeImportTypeDTO(StrEnum):
    SSH = "ssh"
    OFFER = "offer"


class NodeDTO(BaseModel):
    id: StrictStr
    hostname: StrictStr
    import_time: StrictStr
    node_status: StrictStr
    node_type: NodeTypesDTO


class CloudNodeDTO(NodeDTO):
    provider: StrictStr
    instance_type: StrictStr
    price_per_hour: StrictStr
    node_type: NodeTypesDTO = Field(NodeTypesDTO.CLOUD, frozen=True)

    @classmethod
    def from_domain(cls, node: CloudNode) -> CloudNodeDTO:
        return cls(
            id=node.id,
            hostname=node.hostname or "",
            import_time=node.import_time.isoformat() if node.import_time else "N/A",
            node_status=node.node_status,
            node_type=NodeTypesDTO.CLOUD,
            provider=node.provider,
            instance_type=node.instance_type,
            price_per_hour=node.price_per_hour or "N/A",
        )


class SelfManagedNodeDTO(NodeDTO):
    endpoint: StrictStr
    node_type: NodeTypesDTO = Field(NodeTypesDTO.SELF_MANAGED, frozen=True)

    @classmethod
    def from_domain(cls, node: SelfManagedNode) -> SelfManagedNodeDTO:
        return cls(
            id=node.id,
            hostname=node.hostname or "",
            import_time=node.import_time.isoformat() if node.import_time else "N/A",
            node_status=node.node_status,
            node_type=NodeTypesDTO.SELF_MANAGED,
            endpoint=node.endpoint or "",
        )


class NodesListRequestDTO(BaseModel):
    node_type: Optional[NodeTypesDTO] = Field(
        default=None, description="The type of the node"
    )
    status: Optional[AllowedNodeStatusFiltersDTO] = Field(
        default=None, description="The status of the node"
    )


class NodesImportSSHRequestDTO(BaseModel):
    hostname: str = Field(..., description="The hostname of the node")
    endpoint: str = Field(..., description="The endpoint of the node")
    username: str = Field(..., description="The username of the node")
    ssh_key_name: str = Field(..., description="The name of the SSH key to use")
    ssh_key_id: str = Field(..., description="The ID of the SSH key to use")


class NodesImportFromOfferRequestDTO(BaseModel):
    hostname: str = Field(..., description="The hostname of the node")
    offer_id: str = Field(..., description="The ID of the offer to use")
    amount: int = Field(..., description="The amount of nodes to import")

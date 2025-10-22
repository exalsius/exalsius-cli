from __future__ import annotations

from enum import StrEnum
from functools import singledispatch
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.domain import (
    BaseNode,
    CloudNode,
    CloudProvider,
    NodeType,
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


class NodeTypeDTO(StrEnum):
    CLOUD = "cloud"
    SELF_MANAGED = "self-managed"


class NodeDTO(BaseModel):
    id: StrictStr
    hostname: StrictStr
    import_time: StrictStr
    node_status: StrictStr
    node_type: NodeTypeDTO


class CloudNodeDTO(NodeDTO):
    provider: StrictStr
    instance_type: StrictStr
    price_per_hour: StrictStr
    node_type: NodeTypeDTO = Field(NodeTypeDTO.CLOUD, frozen=True)

    @classmethod
    def from_domain(cls, node: CloudNode) -> CloudNodeDTO:
        return cls(
            id=node.id,
            hostname=node.hostname or "",
            import_time=node.import_time.isoformat() if node.import_time else "N/A",
            node_status=node.node_status,
            node_type=NodeTypeDTO.CLOUD,
            provider=CloudProvider(node.provider),
            instance_type=node.instance_type,
            price_per_hour=node.price_per_hour or "N/A",
        )


class SelfManagedNodeDTO(NodeDTO):
    endpoint: StrictStr
    node_type: NodeTypeDTO = Field(NodeTypeDTO.SELF_MANAGED, frozen=True)

    @classmethod
    def from_domain(cls, node: SelfManagedNode) -> SelfManagedNodeDTO:
        return cls(
            id=node.id,
            hostname=node.hostname or "",
            import_time=node.import_time.isoformat() if node.import_time else "N/A",
            node_status=node.node_status,
            node_type=NodeTypeDTO.SELF_MANAGED,
            endpoint=node.endpoint or "",
        )


class NodesListRequestDTO(BaseModel):
    node_type: Optional[NodeTypeDTO] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[CloudProvider] = Field(
        default=None, description="The provider of the node"
    )

    @property
    def domain_node_type(self) -> Optional[NodeType]:
        if self.node_type is None:
            return None
        return NodeType[self.node_type.value.upper()]


class NodesImportSSHRequestDTO(BaseModel):
    hostname: str = Field(..., description="The hostname of the node")
    endpoint: str = Field(..., description="The endpoint of the node")
    username: str = Field(..., description="The username of the node")
    ssh_key_id: str = Field(..., description="The ID of the SSH key to use")


class NodesImportFromOfferRequestDTO(BaseModel):
    hostname: str = Field(..., description="The hostname of the node")
    offer_id: str = Field(..., description="The ID of the offer to use")
    amount: int = Field(..., description="The amount of nodes to import")

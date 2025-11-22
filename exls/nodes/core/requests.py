from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr


class NodeStatusFilter(StrEnum):
    """Enum representing the status of a node."""

    AVAILABLE = "available"
    ADDED = "added"
    FAILED = "failed"


class NodesFilterCriteria(BaseModel):
    """Domain object representing query parameters for nodes."""

    node_type: Optional[StrictStr] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[StrictStr] = Field(
        default=None, description="The provider of the node"
    )
    status: Optional[NodeStatusFilter] = Field(
        default=None, description="The status of the node"
    )


class ImportSelfmanagedNodeRequest(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key to use")


class ImportCloudNodeRequest(BaseModel):
    """Domain object representing parameters for importing a cloud node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")

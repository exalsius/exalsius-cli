from enum import StrEnum
from pathlib import Path
from typing import Optional, Union

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


class SshKeySpecification(BaseModel):
    """Domain object representing parameters for an SSH key."""

    name: StrictStr = Field(..., description="The name of the SSH key")
    key_path: Path = Field(..., description="The path to the SSH key file")


class ImportSelfmanagedNodeRequest(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key: Union[StrictStr, SshKeySpecification] = Field(
        ..., description="The SSH key to use"
    )


class ImportCloudNodeRequest(BaseModel):
    """Domain object representing parameters for importing a cloud node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")

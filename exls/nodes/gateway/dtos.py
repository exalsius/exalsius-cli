from __future__ import annotations

from enum import StrEnum
from typing import Optional

from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from pydantic import BaseModel, Field, PositiveInt, StrictStr


class AllowedNodeStatusFilters(StrEnum):
    """Enum representing the status of a node."""

    AVAILABLE = "AVAILABLE"
    ADDED = "ADDED"
    FAILED = "FAILED"


class NodeFilterParams(BaseModel):
    """Domain object representing query parameters for nodes."""

    node_type: Optional[StrictStr] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[StrictStr] = Field(
        default=None, description="The provider of the node"
    )
    status: Optional[AllowedNodeStatusFilters] = Field(
        default=None, description="The status of the node"
    )


class NodeImportSshParams(BaseModel):
    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key to use")

    # Needs to be moved to mapper if we implement more gateways
    def to_sdk_request(self) -> NodeImportSshRequest:
        return NodeImportSshRequest(
            hostname=self.hostname,
            endpoint=self.endpoint,
            username=self.username,
            ssh_key_id=self.ssh_key_id,
        )


class ImportFromOfferParams(BaseModel):
    """Domain object representing parameters for importing a node from an offer."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")

from enum import StrEnum
from typing import Optional

from pydantic import Field

from exalsius.core.base.commands import BaseRequestDTO


class NodeType(StrEnum):
    """The type of the node."""

    CLOUD = "CLOUD"
    SELF_MANAGED = "SELF_MANAGED"


class CloudProvider(StrEnum):
    """The provider of the node."""

    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"


class NodesBaseRequestDTO(BaseRequestDTO):
    pass


class NodesListRequestDTO(NodesBaseRequestDTO):
    node_type: Optional[NodeType] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[CloudProvider] = Field(
        default=None, description="The provider of the node"
    )


class NodesGetRequestDTO(NodesBaseRequestDTO):
    node_id: str = Field(..., description="The ID of the node to get")


class NodesDeleteRequestDTO(NodesBaseRequestDTO):
    node_id: str = Field(..., description="The ID of the node to delete")


class NodesImportSSHRequestDTO(NodesBaseRequestDTO):
    hostname: str = Field(..., description="The hostname of the node")
    endpoint: str = Field(..., description="The endpoint of the node")
    username: str = Field(..., description="The username of the node")
    ssh_key_id: str = Field(..., description="The ID of the SSH key to use")


class NodesImportFromOfferRequestDTO(NodesBaseRequestDTO):
    hostname: str = Field(..., description="The hostname of the node")
    offer_id: str = Field(..., description="The ID of the offer to use")
    amount: int = Field(..., description="The amount of nodes to import")

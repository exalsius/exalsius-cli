from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.nodes.core.domain import NodeStatus, SelfManagedNode


class NodesFilterCriteria(BaseModel):
    """Domain object representing query parameters for nodes."""

    node_type: Optional[StrictStr] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[StrictStr] = Field(
        default=None, description="The provider of the node"
    )
    status: Optional[NodeStatus] = Field(
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


class ImportSelfmanagedNodeParameters(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key to use")

    @classmethod
    def from_request(
        cls, request: ImportSelfmanagedNodeRequest
    ) -> "ImportSelfmanagedNodeParameters":
        return cls(
            hostname=request.hostname,
            endpoint=request.endpoint,
            username=request.username,
            ssh_key_id=(
                request.ssh_key
                if isinstance(request.ssh_key, str)
                else request.ssh_key.name
            ),
        )


class SelfManagedNodeImportFailure(BaseModel):
    """Domain object representing the failure of importing a node."""

    node: ImportSelfmanagedNodeParameters = Field(
        ..., description="The node that was imported"
    )
    error: Exception = Field(..., description="The error that occurred")
    message: StrictStr = Field(..., description="The message of the error")

    model_config = {"arbitrary_types_allowed": True}


class SelfManagedNodesImportResult(BaseModel):
    """Domain object representing the result of importing multiple nodes."""

    nodes: List[SelfManagedNode] = Field(
        ..., description="The nodes that were imported"
    )
    failures: List[SelfManagedNodeImportFailure] = Field(
        ..., description="The failures that occurred"
    )

    @property
    def is_success(self) -> bool:
        return len(self.failures) == 0

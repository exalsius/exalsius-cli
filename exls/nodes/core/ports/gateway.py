from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
)


class ImportSelfmanagedNodeParameters(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key to use")

    @classmethod
    def from_request(
        cls, request: ImportSelfmanagedNodeRequest
    ) -> ImportSelfmanagedNodeParameters:
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


class ImportCloudNodeParameters(BaseModel):
    """Domain object representing parameters for importing a cloud node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")


class SelfManagedNodeImportFailure(BaseModel):
    """Domain object representing the failure of importing a node."""

    node: ImportSelfmanagedNodeParameters = Field(
        ..., description="The node that was imported"
    )
    error: Exception = Field(..., description="The error that occurred")
    message: StrictStr = Field(..., description="The message of the error")


class INodesGateway(ABC):
    @abstractmethod
    def list(self, filter: NodesFilterCriteria) -> List[BaseNode]: ...

    @abstractmethod
    def get(self, node_id: str) -> BaseNode: ...

    @abstractmethod
    def delete(self, node_id: str) -> str: ...

    @abstractmethod
    def import_selfmanaged_node(
        self, request: ImportSelfmanagedNodeParameters
    ) -> str: ...

    @abstractmethod
    def import_cloud_nodes(self, request: ImportCloudNodeParameters) -> List[str]: ...

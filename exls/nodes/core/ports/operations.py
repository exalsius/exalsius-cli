from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
)


class ImportSelfmanagedNodeParameters(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key to use")

    @classmethod
    def from_request(
        cls, request: ImportSelfmanagedNodeRequest
    ) -> ImportSelfmanagedNodeParameters:
        assert isinstance(request.ssh_key, str), "SSH key ID must be provided"
        return cls(
            hostname=request.hostname,
            endpoint=request.endpoint,
            username=request.username,
            ssh_key_id=request.ssh_key,
        )

    @classmethod
    def to_request(
        cls, parameters: ImportSelfmanagedNodeParameters
    ) -> ImportSelfmanagedNodeRequest:
        return ImportSelfmanagedNodeRequest(
            hostname=parameters.hostname,
            endpoint=parameters.endpoint,
            username=parameters.username,
            ssh_key=parameters.ssh_key_id,
        )


class NodesOperations(ABC):
    @abstractmethod
    def import_selfmanaged_node(
        self, parameters: ImportSelfmanagedNodeParameters
    ) -> str: ...

    # We leake the domain's request here, which is fine since they
    # are identical
    @abstractmethod
    def import_cloud_nodes(self, parameters: ImportCloudNodeRequest) -> List[str]: ...

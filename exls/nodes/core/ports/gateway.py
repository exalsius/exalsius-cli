from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    NodesFilterCriteria,
)


class ImportSelfmanagedNodeParameters(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key to use")


class ImportCloudNodeParameters(BaseModel):
    """Domain object representing parameters for importing a cloud node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")


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

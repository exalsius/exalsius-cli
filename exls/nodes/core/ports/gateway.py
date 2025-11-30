from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    ImportSelfmanagedNodeParameters,
    NodesFilterCriteria,
)


class ImportCloudNodeParameters(BaseModel):
    """Domain object representing parameters for importing a cloud node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: PositiveInt = Field(..., description="The amount of nodes to import")


class INodesGateway(ABC):
    @abstractmethod
    def list(self, filter: Optional[NodesFilterCriteria]) -> List[BaseNode]: ...

    @abstractmethod
    def get(self, node_id: str) -> BaseNode: ...

    @abstractmethod
    def delete(self, node_id: str) -> str: ...

    @abstractmethod
    def import_selfmanaged_node(
        self, parameters: ImportSelfmanagedNodeParameters
    ) -> str: ...

    @abstractmethod
    def import_cloud_nodes(
        self, parameters: ImportCloudNodeParameters
    ) -> List[str]: ...

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import ClusterNode, ClusterNodeResources
from exls.clusters.core.requests import ClusterNodeSpecification


class ClusterNodeData(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key of the node")
    status: StrictStr = Field(..., description="The status of the node")
    endpoint: Optional[StrictStr] = Field(
        default=None, description="The endpoint of the node"
    )
    resources: ClusterNodeResources = Field(
        ..., description="The resources of the node"
    )


class ClusterNodeImportIssue(BaseModel):
    node_specification: ClusterNodeSpecification = Field(
        ..., description="The node specification"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ClusterNodesImportResult(BaseModel):
    nodes: List[ClusterNode] = Field(..., description="The imported nodes")
    issues: List[ClusterNodeImportIssue] = Field(
        ..., description="The issues with the imported nodes"
    )


class NodesProvider(ABC):
    @abstractmethod
    def list_nodes(self) -> List[ClusterNodeData]: ...

    @abstractmethod
    def list_available_nodes(self) -> List[ClusterNode]: ...

    @abstractmethod
    def import_nodes(
        self,
        nodes_specs: List[ClusterNodeSpecification],
        wait_for_available: bool = False,
    ) -> ClusterNodesImportResult: ...

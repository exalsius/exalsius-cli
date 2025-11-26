from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import ClustersNode, NodeStatus
from exls.clusters.core.requests import NodeSpecification


class NodeImportIssue(BaseModel):
    node_spec_repr: Optional[StrictStr] = Field(
        ..., description="The representation of the node specification"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ClusterNodeProviderNode(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key: StrictStr = Field(..., description="The SSH key of the node")
    status: NodeStatus = Field(..., description="The status of the node")


class NodesImportResult(BaseModel):
    nodes: List[ClustersNode] = Field(..., description="The imported nodes")
    issues: List[NodeImportIssue] = Field(
        ..., description="The issues with the imported nodes"
    )


class INodesProvider(ABC):
    @abstractmethod
    def list_nodes(self) -> List[ClusterNodeProviderNode]: ...

    @abstractmethod
    def get_node(self, node_id: str) -> ClusterNodeProviderNode: ...

    @abstractmethod
    def import_nodes(
        self, requests: List[NodeSpecification], wait_for_available: bool = False
    ) -> NodesImportResult: ...

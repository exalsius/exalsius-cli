from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import (
    AssignedClusterNode,
    ClusterNode,
)
from exls.clusters.core.requests import NodeSpecification


class ClusterNodeImportIssue(BaseModel):
    node_spec_repr: Optional[StrictStr] = Field(
        ..., description="The representation of the node specification"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ClusterNodesImportResult(BaseModel):
    nodes: List[AssignedClusterNode] = Field(..., description="The imported nodes")
    issues: List[ClusterNodeImportIssue] = Field(
        ..., description="The issues with the imported nodes"
    )


class INodesProvider(ABC):
    @abstractmethod
    def list_nodes(self) -> List[ClusterNode]: ...

    @abstractmethod
    def import_nodes(
        self, nodes_specs: List[NodeSpecification], wait_for_available: bool = False
    ) -> ClusterNodesImportResult: ...

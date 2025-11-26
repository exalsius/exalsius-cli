from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.core.ports.gateway import SelfManagedNodeImportFailure


class NodeStatus(StrEnum):
    DISCOVERING = "DISCOVERING"
    AVAILABLE = "AVAILABLE"
    ADDED = "ADDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> NodeStatus:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class BaseNode(BaseModel):
    """Domain object representing a node."""

    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    import_time: Optional[datetime] = Field(
        ..., description="The time the node was imported"
    )
    node_status: NodeStatus = Field(..., description="The status of the node")


class CloudNode(BaseNode):
    """Domain object representing a cloud node."""

    provider: StrictStr = Field(..., description="The provider of the node")
    instance_type: StrictStr = Field(..., description="The instance type of the node")
    price_per_hour: StrictStr = Field(..., description="The price per hour of the node")


class SelfManagedNode(BaseNode):
    """Domain object representing a self-managed node."""

    endpoint: Optional[StrictStr] = Field(
        default=None, description="The endpoint of the node"
    )


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

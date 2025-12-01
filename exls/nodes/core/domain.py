from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, StrictStr


class NodeStatus(StrEnum):
    DISCOVERING = "DISCOVERING"
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
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
    status: NodeStatus = Field(..., description="The status of the node")


class CloudNode(BaseNode):
    """Domain object representing a cloud node."""

    provider: StrictStr = Field(..., description="The provider of the node")
    instance_type: StrictStr = Field(..., description="The instance type of the node")
    price_per_hour: StrictStr = Field(..., description="The price per hour of the node")


class SelfManagedNode(BaseNode):
    """Domain object representing a self-managed node."""

    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key")
    ssh_key_name: Optional[StrictStr] = Field(
        default="", description="The name of the SSH key"
    )
    username: StrictStr = Field(..., description="The username of the node")
    endpoint: Optional[StrictStr] = Field(
        default=None, description="The endpoint of the node"
    )

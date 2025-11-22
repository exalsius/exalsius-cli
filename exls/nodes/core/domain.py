from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr


class BaseNode(BaseModel):
    """Domain object representing a node."""

    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    import_time: Optional[datetime] = Field(
        ..., description="The time the node was imported"
    )
    node_status: StrictStr = Field(..., description="The status of the node")


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

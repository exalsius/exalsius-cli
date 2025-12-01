from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr


class NodeDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    import_time: Optional[datetime] = Field(
        ..., description="The time the node was imported"
    )
    node_status: StrictStr = Field(..., description="The status of the node")


class CloudNodeDTO(NodeDTO):
    provider: StrictStr = Field(..., description="The provider of the node")
    instance_type: StrictStr = Field(..., description="The instance type of the node")
    price_per_hour: StrictStr = Field(..., description="The price per hour of the node")


class SelfManagedNodeDTO(NodeDTO):
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key")
    ssh_key_name: StrictStr = Field(..., description="The name of the SSH key")
    endpoint: Optional[StrictStr] = Field(..., description="The endpoint of the node")

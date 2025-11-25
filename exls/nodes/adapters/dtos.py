from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.adapters.values import (
    AllowedNodeStatusFilter,
    NodeTypesDTO,
)


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
    endpoint: Optional[StrictStr] = Field(..., description="The endpoint of the node")


class NodesListRequestDTO(BaseModel):
    node_type: Optional[NodeTypesDTO] = Field(
        default=None, description="The type of the node"
    )
    status: Optional[AllowedNodeStatusFilter] = Field(
        default=None, description="The status of the node"
    )

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr


class Service(BaseModel):
    id: StrictStr = Field(..., description="The ID of the service")
    name: StrictStr = Field(..., description="The name of the service")
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    service_template: StrictStr = Field(
        ..., description="The name of the service template"
    )
    created_at: Optional[datetime] = Field(
        None, description="The creation date of the service"
    )

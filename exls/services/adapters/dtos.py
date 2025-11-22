from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr


class ServiceDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the service")
    name: StrictStr = Field(..., description="The name of the service")
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name: StrictStr = Field(
        ..., description="The name of the service template"
    )
    created_at: Optional[datetime] = Field(
        ..., description="The creation date of the service"
    )

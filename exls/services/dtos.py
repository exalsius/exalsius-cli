from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.services.domain import Service


class ServiceListRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class ServiceDTO(BaseModel):
    id: StrictStr
    name: StrictStr
    cluster_id: StrictStr
    service_template: StrictStr
    created_at: Optional[datetime]

    @classmethod
    def from_domain(cls, service: Service) -> ServiceDTO:
        return cls(
            id=service.id,
            name=service.name,
            cluster_id=service.cluster_id,
            service_template=service.service_template,
            created_at=service.created_at,
        )

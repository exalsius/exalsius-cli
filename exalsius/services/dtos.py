from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exalsius.services.domain import BaseServiceTemplate, Service


class ServiceListRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class ServiceDeployRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the service")
    service_template: BaseServiceTemplate = Field(
        ..., description="The service template factory to use"
    )


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


class CreateServiceRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the service")
    service_template: BaseServiceTemplate = Field(
        ..., description="The service template factory to use"
    )

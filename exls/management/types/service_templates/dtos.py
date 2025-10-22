from __future__ import annotations

from pydantic import BaseModel, Field

from exls.management.types.service_templates.domain import ServiceTemplate


class ListServiceTemplatesRequestDTO(BaseModel):
    pass


class ServiceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the service template")
    description: str = Field(description="The description of the service template")
    variables: str = Field(description="The variables of the service template")

    @classmethod
    def from_domain(cls, domain_obj: ServiceTemplate) -> ServiceTemplateDTO:
        return cls(
            name=domain_obj.name,
            description=domain_obj.description,
            variables=", ".join(domain_obj.variables),
        )

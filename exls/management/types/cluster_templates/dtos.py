from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.management.types.cluster_templates.domain import ClusterTemplate


class ListClusterTemplatesRequestDTO(BaseModel):
    pass


class ClusterTemplateDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster template")
    description: Optional[StrictStr] = Field(
        None, description="The description of the cluster template"
    )
    k8s_version: Optional[StrictStr] = Field(
        None, description="The Kubernetes version of the cluster template"
    )

    @classmethod
    def from_domain(cls, domain_obj: ClusterTemplate) -> ClusterTemplateDTO:
        return cls(
            name=domain_obj.name,
            description=domain_obj.description,
            k8s_version=domain_obj.k8s_version,
        )

from __future__ import annotations

from pydantic import BaseModel, Field

from exls.management.types.workspace_templates.domain import WorkspaceTemplate


class ListWorkspaceTemplatesRequestDTO(BaseModel):
    pass


class WorkspaceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the workspace template")
    description: str = Field(description="The description of the workspace template")
    variables: str = Field(description="The variables of the workspace template")

    @classmethod
    def from_domain(cls, domain_obj: WorkspaceTemplate) -> WorkspaceTemplateDTO:
        return cls(
            name=domain_obj.name,
            description=domain_obj.description or "",
            variables=", ".join(domain_obj.variables.keys()),
        )

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field

from exls.management.types.workspace_templates.domain import WorkspaceTemplate


class ListWorkspaceTemplatesRequestDTO(BaseModel):
    pass


class WorkspaceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the workspace template")
    description: str = Field(description="The description of the workspace template")
    variables: Dict[str, Any] = Field(
        description="The variables of the workspace template with default values"
    )

    @classmethod
    def from_domain(cls, domain_obj: WorkspaceTemplate) -> WorkspaceTemplateDTO:
        return cls(
            name=domain_obj.name,
            description=domain_obj.description or "",
            variables=domain_obj.variables,
        )

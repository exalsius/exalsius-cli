from pydantic import BaseModel, Field

from exalsius.management.models import BaseManagementRequestDTO


class ListWorkspaceTemplatesRequestDTO(BaseManagementRequestDTO):
    pass


class RenderableWorkspaceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the workspace template")
    description: str = Field(description="The description of the workspace template")
    variables: str = Field(description="The variables of the workspace template")

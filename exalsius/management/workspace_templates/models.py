from pydantic import BaseModel, Field

from exalsius.core.base.commands import BaseRequest


class ListWorkspaceTemplatesRequestDTO(BaseRequest):
    pass


class RenderableWorkspaceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the workspace template")
    description: str = Field(description="The description of the workspace template")
    variables: str = Field(description="The variables of the workspace template")

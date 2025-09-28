from pydantic import BaseModel, Field

from exalsius.management.models import BaseManagementRequestDTO


class ListServiceTemplatesRequestDTO(BaseManagementRequestDTO):
    pass


class RenderableServiceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the service template")
    description: str = Field(description="The description of the service template")
    variables: str = Field(description="The variables of the service template")

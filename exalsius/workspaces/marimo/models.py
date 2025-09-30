from typing import ClassVar, Optional

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.workspaces.models import WorkspaceBaseTemplateDTO


class MarimoWorkspaceVariablesDTO(BaseSettings):
    deployment_name: str = Field(..., description="The name of the deployment")
    deployment_image: Optional[str] = Field(
        None, description="The image of the deployment"
    )
    ephemeral_storage_gb: int = Field(
        ...,
        description="The amount of ephemeral storage in GB to add to the workspace pod",
    )

    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class MarimoWorkspaceTemplateDTO(WorkspaceBaseTemplateDTO):
    name: ClassVar[str] = "marimo-workspace-template"

    variables: MarimoWorkspaceVariablesDTO = Field(
        ..., description="The variables of the marimo workspace template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = WorkspaceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )
        return template

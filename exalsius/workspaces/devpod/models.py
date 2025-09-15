from typing import Literal

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.workspaces.models import WorkspaceBaseTemplateDTO


class DevPodWorkspaceVariablesDTO(BaseSettings):
    deployment_name: str = Field(..., description="The name of the deployment")
    deployment_image: str = Field(..., description="The image of the deployment")
    ephemeral_storage_gb: int = Field(
        ...,
        description="The amount of ephemeral storage in GB to add to the workspace pod",
    )

    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class DevPodWorkspaceTemplateDTO(WorkspaceBaseTemplateDTO):
    name: Literal["vscode-devcontainer-template"] = "vscode-devcontainer-template"
    variables: DevPodWorkspaceVariablesDTO = Field(
        ..., description="The variables of the template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = WorkspaceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True),
        )
        return template

from typing import ClassVar

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.workspaces.models import WorkspaceBaseTemplateDTO


class JupyterWorkspaceVariablesDTO(BaseSettings):
    deployment_name: str = Field(..., description="The name of the deployment")
    deployment_image: str = Field(..., description="The image of the deployment")
    notebook_password: str = Field(
        ..., description="The password of the Jupyter notebook"
    )
    ephemeral_storage_gb: int = Field(
        ...,
        description="The amount of ephemeral storage in GB to add to the workspace pod",
    )

    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class JupyterWorkspaceTemplateDTO(WorkspaceBaseTemplateDTO):
    name: ClassVar[str] = "jupyter-notebook-template"

    variables: JupyterWorkspaceVariablesDTO = Field(
        ..., description="The variables of the jupyter notebook template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = WorkspaceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )
        return template

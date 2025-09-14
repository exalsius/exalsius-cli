from typing import Literal, Optional

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.workspaces.models import WorkspaceBaseTemplateDTO


class LLMInferenceWorkspaceVariablesDTO(BaseSettings):
    deployment_name: str = Field(..., description="The name of the deployment")
    deployment_image: str = Field(..., description="The image of the deployment")
    huggingface_model: str = Field(
        ..., description="The HuggingFace model to use for the workspace"
    )
    huggingface_token: Optional[str] = Field(
        None, description="The HuggingFace token to use for the workspace"
    )
    num_model_replicas: int = Field(
        ..., description="The number of model replicas to use for the workspace"
    )
    tensor_parallel_size: int = Field(
        ..., description="The tensor parallel size to use for the workspace"
    )
    pipeline_parallel_size: int = Field(
        ..., description="The pipeline parallel size to use for the workspace"
    )
    cpu_per_actor: int = Field(
        ..., description="The number of CPU cores to use per actor"
    )
    gpu_per_actor: int = Field(..., description="The number of GPUs to use per actor")
    ephemeral_storage_gb: int = Field(
        ...,
        description="The amount of ephemeral storage in GB to add to the workspace pod",
    )

    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class LLMInferenceWorkspaceTemplateDTO(WorkspaceBaseTemplateDTO):
    name: Literal["ray-llm-service-template"] = "ray-llm-service-template"
    variables: LLMInferenceWorkspaceVariablesDTO = Field(
        ..., description="The variables of the llm inference template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = WorkspaceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )
        return template

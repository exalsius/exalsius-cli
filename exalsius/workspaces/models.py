import datetime
import enum
from abc import abstractmethod
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.resource_pool import ResourcePool
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import BaseModel, Field

from exalsius.core.base.models import BaseRequestDTO


class WorkspaceType(str, enum.Enum):
    POD = "POD"
    JUPYTER = "JUPYTER"
    LLM_INFERENCE = "LLM_INFERENCE"


class WorkspacesBaseRequestDTO(BaseRequestDTO):
    api: WorkspacesApi = Field(..., description="The API client")


class WorkspacesListRequestDTO(WorkspacesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")


class GetWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")


class WorkspaceBaseTemplateDTO(BaseModel):
    name: str = Field(..., description="The name of the workspace template")

    @abstractmethod
    def to_api_model(self) -> WorkspaceTemplate:
        pass


class WorkspacePodTemplateDTO(WorkspaceBaseTemplateDTO):
    def to_api_model(self) -> WorkspaceTemplate:
        return WorkspaceTemplate(
            name=self.name,
            variables={},
        )


class WorkspaceJupyterTemplateDTO(WorkspaceBaseTemplateDTO):
    jupyter_password: Optional[str] = Field(
        None, description="The password of the Jupyter notebook"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        variables = {}
        if self.jupyter_password is not None:
            variables["jupyterPassword"] = self.jupyter_password
        return WorkspaceTemplate(
            name=self.name,
            variables=variables,
        )


class WorkspaceLLMInferenceTemplateDTO(WorkspaceBaseTemplateDTO):
    huggingface_model: str = Field(
        ..., description="The model of the workspace template"
    )
    huggingface_token: Optional[str] = Field(
        None, description="The token of the workspace template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        variables = {"huggingfaceModel": self.huggingface_model}
        if self.huggingface_token is not None:
            variables["huggingfaceToken"] = self.huggingface_token
        return WorkspaceTemplate(
            name=self.name,
            variables=variables,
        )


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(1, description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    cpu_cores: int = Field(16, description="The number of CPU cores")
    memory_gb: int = Field(32, description="The amount of memory in GB")
    storage_gb: int = Field(200, description="The amount of storage in GB")

    def to_api_model(self) -> ResourcePool:
        return ResourcePool(
            gpu_count=self.gpu_count,
            gpu_type=self.gpu_type,
            cpu_cores=self.cpu_cores,
            memory_gb=self.memory_gb,
            storage_gb=self.storage_gb,
        )


class CreateWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    name: str = Field(..., description="The name of the workspace")
    cluster_id: str = Field(..., description="The ID of the cluster")
    resources: ResourcePoolDTO = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime.datetime] = Field(
        None, description="The date and time the workspace will be deleted"
    )
    template: WorkspaceBaseTemplateDTO = Field(
        ..., description="The template of the workspace"
    )

    def to_api_model(self) -> WorkspaceCreateRequest:
        return WorkspaceCreateRequest(
            cluster_id=self.cluster_id,
            name=self.name,
            resources=self.resources.to_api_model(),
            template=self.template.to_api_model(),
            description=self.description,
            to_be_deleted_at=self.to_be_deleted_at,
        )


class CreatePodWorkspaceRequestDTO(CreateWorkspaceRequestDTO):
    template: WorkspacePodTemplateDTO = Field(
        ..., description="The template of the workspace"
    )


class CreateJupyterWorkspaceRequestDTO(CreateWorkspaceRequestDTO):
    template: WorkspaceJupyterTemplateDTO = Field(
        ..., description="The template of the workspace"
    )


class CreateLLMInferenceWorkspaceRequestDTO(CreateWorkspaceRequestDTO):
    template: WorkspaceLLMInferenceTemplateDTO = Field(
        ..., description="The template of the workspace"
    )


class DeleteWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")

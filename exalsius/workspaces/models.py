import datetime
from abc import abstractmethod
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.resource_pool import ResourcePool
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import BaseModel, Field

from exalsius.core.base.models import BaseRequestDTO
from exalsius.utils import commons


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


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")

    def to_api_model(self) -> ResourcePool:
        return ResourcePool(
            gpu_count=self.gpu_count,
            gpu_type=self.gpu_type,
            gpu_vendor=self.gpu_vendor,
            cpu_cores=self.cpu_cores,
            memory_gb=self.memory_gb,
            storage_gb=self.storage_gb,
        )


class CreateWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the workspace")
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    resources: ResourcePoolDTO = Field(
        ..., description="The resources of the workspace"
    )
    template: WorkspaceBaseTemplateDTO = Field(
        ..., description="The template of the workspace"
    )
    to_be_deleted_at: Optional[datetime.datetime] = Field(
        None, description="The date and time the workspace will be deleted"
    )

    def to_api_model(self) -> WorkspaceCreateRequest:
        template: WorkspaceTemplate = self.template.to_api_model()
        template.variables["deploymentName"] = commons.generate_random_name(
            prefix=self.name, slug_length=2
        )

        return WorkspaceCreateRequest(
            cluster_id=self.cluster_id,
            name=self.name,
            resources=self.resources.to_api_model(),
            template=template,
            description=self.description,
            to_be_deleted_at=self.to_be_deleted_at,
        )


class DeleteWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")

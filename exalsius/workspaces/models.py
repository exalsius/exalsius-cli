import datetime
from abc import ABC, abstractmethod
from typing import ClassVar, Optional

from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import BaseModel, Field

from exalsius.core.base.commands import BaseRequestDTO
from exalsius.utils import commons


class WorkspacesListRequestDTO(BaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")


class GetWorkspaceRequestDTO(BaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")


class WorkspaceBaseTemplateDTO(BaseModel, ABC):
    name: ClassVar[str] = "workspace-template"

    @abstractmethod
    def to_api_model(self) -> WorkspaceTemplate: ...


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")

    def to_api_model(self) -> Hardware:
        return Hardware(
            gpu_count=self.gpu_count,
            gpu_type=self.gpu_type,
            gpu_vendor=self.gpu_vendor,
            cpu_cores=self.cpu_cores,
            memory_gb=self.memory_gb,
            storage_gb=self.storage_gb,
        )


class CreateWorkspaceRequestDTO(BaseRequestDTO):
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


class DeleteWorkspaceRequestDTO(BaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")


class WorkspaceAccessInformationDTO(BaseModel):
    workspace_id: str = Field(..., description="The ID of the workspace")
    access_type: str = Field(..., description="The type of access")
    access_endpoint: str = Field(
        ..., description="The access endpoint of the workspace"
    )

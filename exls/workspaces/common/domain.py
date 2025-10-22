from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from exalsius_api_client.models.hardware import Hardware as SdkResourcePool
from exalsius_api_client.models.workspace import Workspace as SdkWorkspace
from exalsius_api_client.models.workspace_access_information import (
    WorkspaceAccessInformation as SdkWorkspaceAccessInformation,
)
from pydantic import BaseModel, Field, StrictStr

from exls.workspaces.common.dtos import WorkspaceResourcesRequestDTO


class WorkspaceAccessInformation(BaseModel):
    sdk_model: SdkWorkspaceAccessInformation = Field(
        ..., description="The SDK model of the workspace access information"
    )

    @property
    def access_type(self) -> str:
        return self.sdk_model.access_type

    @property
    def access_protocol(self) -> str:
        return self.sdk_model.access_protocol

    @property
    def external_ip(self) -> str:
        return (
            self.sdk_model.external_ip
            if self.sdk_model.external_ip is not None
            else "N/A"
        )

    @property
    def port_number(self) -> int:
        return self.sdk_model.port_number

    @property
    def endpoint(self) -> str:
        if self.external_ip and self.port_number:
            return f"{self.access_protocol.lower()}://{self.external_ip}:{self.port_number}"
        return "N/A"


class WorkspaceFilterParams(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class Workspace(BaseModel):
    sdk_model: SdkWorkspace = Field(..., description="The SDK model of the workspace")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def cluster_id(self) -> StrictStr:
        return self.sdk_model.cluster_id

    @property
    def name(self) -> StrictStr:
        return self.sdk_model.name

    @property
    def workspace_status(self) -> str:
        if self.sdk_model.workspace_status is None:
            raise ValueError("Workspace status is None")
        return self.sdk_model.workspace_status

    @property
    def created_at(self) -> datetime:
        if self.sdk_model.created_at is None:
            raise ValueError("Created at is None")
        return self.sdk_model.created_at

    @property
    def access_information(self) -> List[WorkspaceAccessInformation]:
        if self.sdk_model.access_information is None:
            return []
        return [
            WorkspaceAccessInformation(sdk_model=info)
            for info in self.sdk_model.access_information
        ]


class Resources(BaseModel):
    sdk_model: SdkResourcePool = Field(
        ..., description="The SDK model of the resources"
    )

    @property
    def gpu_count(self) -> int:
        return self.sdk_model.gpu_count or 0

    @property
    def gpu_type(self) -> Optional[str]:
        return self.sdk_model.gpu_type

    @property
    def gpu_vendor(self) -> Optional[str]:
        return self.sdk_model.gpu_vendor

    @property
    def cpu_cores(self) -> int:
        return self.sdk_model.cpu_cores or 0

    @property
    def memory_gb(self) -> int:
        return self.sdk_model.memory_gb or 0

    @property
    def storage_gb(self) -> int:
        return self.sdk_model.storage_gb or 0


class ResourceRequested(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    pvc_storage_gb: int = Field(..., description="The amount of PVC storage in GB")
    ephemeral_storage_gb: Optional[int] = Field(
        None, description="The amount of ephemeral storage in GB"
    )

    @classmethod
    def from_request_dto(
        cls, request_dto: WorkspaceResourcesRequestDTO
    ) -> ResourceRequested:
        return ResourceRequested(
            gpu_count=request_dto.gpu_count,
            gpu_type=request_dto.gpu_type,
            gpu_vendor=request_dto.gpu_vendor,
            cpu_cores=request_dto.cpu_cores,
            memory_gb=request_dto.memory_gb,
            pvc_storage_gb=request_dto.pvc_storage_gb,
            ephemeral_storage_gb=request_dto.ephemeral_storage_gb,
        )


class DeployWorkspaceParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_id: StrictStr = Field(..., description="The ID of the template")
    name: StrictStr = Field(..., description="The name of the workspace")
    resources: ResourceRequested = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        None, description="The date and time when the workspace should be deleted"
    )

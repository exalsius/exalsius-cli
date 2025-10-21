from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from exalsius.clusters.domain import Cluster
from exalsius.workspaces.domain import Resources, Workspace, WorkspaceAccessInformation


class ListWorkspacesRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class WorkspaceDTO(BaseModel):
    workspace_id: str = Field(..., description="The ID of the workspace")
    cluster_id: str = Field(..., description="The ID of the cluster")
    cluster_name: str = Field(..., description="The name of the cluster")
    workspace_name: str = Field(..., description="The name of the workspace")
    workspace_status: str = Field(..., description="The status of the workspace")
    workspace_created_at: datetime = Field(
        ..., description="The creation date of the workspace"
    )
    workspace_access_information: Optional[WorkspaceAccessInformationDTO] = Field(
        None, description="The access information of the workspace"
    )

    @classmethod
    def from_domain(cls, workspace: Workspace, cluster: Cluster) -> WorkspaceDTO:
        access_information: WorkspaceAccessInformation | None = None
        if workspace.access_information:
            access_information = workspace.access_information[0]
        return cls(
            workspace_id=workspace.id,
            cluster_id=cluster.id,
            cluster_name=cluster.name,
            workspace_name=workspace.name,
            workspace_status=workspace.workspace_status,
            workspace_created_at=workspace.created_at,
            workspace_access_information=WorkspaceAccessInformationDTO.from_domain(
                access_information, workspace.id
            )
            if access_information
            else None,
        )


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")

    @classmethod
    def from_domain(cls, resources: Resources) -> ResourcePoolDTO:
        return cls(
            gpu_count=resources.gpu_count,
            gpu_type=resources.gpu_type,
            gpu_vendor=resources.gpu_vendor,
            cpu_cores=resources.cpu_cores,
            memory_gb=resources.memory_gb,
            storage_gb=resources.storage_gb,
        )


class WorkspaceResourcesRequestDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    pvc_storage_gb: int = Field(..., description="The amount of PVC storage in GB")
    ephemeral_storage_gb: Optional[int] = Field(
        None, description="The amount of ephemeral storage in GB"
    )


class DeployWorkspaceRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the workspace")
    resources: WorkspaceResourcesRequestDTO = Field(
        ..., description="The resources of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        None, description="The date and time when the workspace should be deleted"
    )


class WorkspaceAccessInformationDTO(BaseModel):
    workspace_id: str = Field(..., description="The ID of the workspace")
    access_type: str = Field(..., description="The type of access")
    access_endpoint: str = Field(
        ..., description="The access endpoint of the workspace"
    )

    @classmethod
    def from_domain(
        cls, domain_obj: WorkspaceAccessInformation, workspace_id: str
    ) -> WorkspaceAccessInformationDTO:
        return cls(
            workspace_id=workspace_id,
            access_type=domain_obj.access_type,
            access_endpoint=domain_obj.endpoint,
        )

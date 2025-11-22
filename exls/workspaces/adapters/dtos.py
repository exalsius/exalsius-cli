from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ListWorkspacesRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class WorkspaceAccessInformationDTO(BaseModel):
    access_type: str = Field(..., description="The type of access")
    access_endpoint: str = Field(
        ..., description="The access endpoint of the workspace"
    )


class WorkspaceDTO(BaseModel):
    id: str = Field(..., description="The ID of the workspace")
    name: str = Field(..., description="The name of the workspace")
    cluster_id: str = Field(..., description="The ID of the cluster")
    template_name: str = Field(..., description="The name of the workspace template")
    status: str = Field(..., description="The status of the workspace")
    created_at: Optional[datetime] = Field(
        ..., description="The creation date of the workspace"
    )
    access_information: List[WorkspaceAccessInformationDTO] = Field(
        ..., description="The access information of the workspace"
    )


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")


class WorkspaceResourcesRequestDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    pvc_storage_gb: int = Field(..., description="The amount of PVC storage in GB")


class DeployWorkspaceRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")
    cluster_name: str = Field(..., description="The name of the cluster")
    workspace_name: str = Field(..., description="The name of the workspace")
    workspace_template_name: str = Field(
        ..., description="The name of the workspace template"
    )
    resources: WorkspaceResourcesRequestDTO = Field(
        ..., description="The resources of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        None, description="The date and time when the workspace should be deleted"
    )
    variables: Dict[str, Any] = Field(..., description="The variables of the workspace")

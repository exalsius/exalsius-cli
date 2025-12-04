from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ListWorkspacesRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")


class WorkspaceAccessInformationDTO(BaseModel):
    type: Optional[str] = Field(..., description="The type of access")
    protocol: Optional[str] = Field(..., description="The protocol of the access")
    ip: Optional[str] = Field(..., description="The IP address of the workspace")
    port: Optional[int] = Field(..., description="The port of the access")


class WorkspaceDTO(BaseModel):
    id: str = Field(..., description="The ID of the workspace")
    name: str = Field(..., description="The name of the workspace")
    cluster_name: str = Field(..., description="The name of the cluster")
    template_name: str = Field(..., description="The name of the workspace template")
    status: str = Field(..., description="The status of the workspace")
    created_at: Optional[datetime] = Field(
        ..., description="The creation date of the workspace"
    )
    access_information: Optional[WorkspaceAccessInformationDTO] = Field(
        ..., description="The access information of the workspace"
    )

    @property
    def access(self) -> Optional[str]:
        if (
            self.access_information
            and self.access_information.ip
            and self.access_information.port
            and self.access_information.protocol
        ):
            if self.access_information.protocol.upper() == "SSH":
                return f"ssh -p {self.access_information.port} dev@{self.access_information.ip}"
            else:
                return f"{self.access_information.protocol.lower()}://{self.access_information.ip}:{self.access_information.port}"
        return "N/A"


class SingleNodeWorkspaceDTO(WorkspaceDTO):
    pass


class MultiNodeWorkspaceDTO(WorkspaceDTO):
    total_nodes: int = Field(..., description="The total number of nodes")
    gpu_types: str = Field(..., description="The types of the GPUs")


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
    storage_gb: int = Field(..., description="The amount of storage in GB")

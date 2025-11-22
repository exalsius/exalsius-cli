from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, StrictStr


class WorkspaceStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class WorkspaceAccessInformation(BaseModel):
    access_type: str = Field(..., description="The access type")
    access_protocol: str = Field(..., description="The access protocol")
    external_ip: Optional[str] = Field(None, description="The external IP")
    port_number: int = Field(..., description="The port number")

    @property
    def endpoint(self) -> str:
        if self.external_ip and self.port_number:
            return f"{self.access_protocol.lower()}://{self.external_ip}:{self.port_number}"
        return "N/A"


class Workspace(BaseModel):
    id: StrictStr = Field(..., description="The ID of the workspace")
    name: StrictStr = Field(..., description="The name of the workspace")
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name: StrictStr = Field(
        ..., description="The name of the workspace template"
    )
    status: WorkspaceStatus = Field(..., description="The status of the workspace")
    created_at: Optional[datetime] = Field(
        None, description="The creation date of the workspace"
    )
    access_information: List[WorkspaceAccessInformation] = Field(
        default_factory=list, description="The access information of the workspace"
    )


class Resources(BaseModel):
    gpu_count: int = Field(default=0, description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of GPU")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPU")
    cpu_cores: int = Field(default=0, description="The number of CPU cores")
    memory_gb: int = Field(default=0, description="The amount of memory in GB")
    storage_gb: int = Field(default=0, description="The amount of storage in GB")


class RequestedResources(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    pvc_storage_gb: int = Field(..., description="The amount of PVC storage in GB")


class DeployWorkspaceRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name: StrictStr = Field(..., description="The ID of the template")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    resources: RequestedResources = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        None, description="The date and time when the workspace should be deleted"
    )
    variables: Dict[str, Any] = Field(..., description="The variables of the workspace")

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field, StrictStr


class WorkspaceClusterStatus(StrEnum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    READY = "READY"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceClusterStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


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


class WorkspaceGPUVendor(StrEnum):
    AMD = "AMD"
    NVIDIA = "NVIDIA"
    NO_GPU = "NO_GPU"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceGPUVendor:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class WorkspaceAccessType(StrEnum):
    NODE_PORT = "NODE_PORT"
    INGRESS = "INGRESS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceAccessType:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class WorkspaceAccessInformation(BaseModel):
    access_type: WorkspaceAccessType = Field(..., description="The access type")
    access_protocol: str = Field(..., description="The access protocol")
    external_ips: List[str] = Field(
        default_factory=list, description="The external IPs"
    )
    port_number: int = Field(..., description="The port number")

    @property
    def endpoint(self) -> str:
        if not self.external_ips or not self.port_number:
            return "N/A"

        # edge case for SSH access
        # TODO: move this to the API at some point (?)
        if self.access_protocol.upper() == "SSH":
            return f"ssh -p {self.port_number} dev@{self.external_ips[0]}"

        return f"{self.access_protocol.lower()}://{self.external_ips[0]}:{self.port_number}"


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
        default_factory=lambda: cast(List[WorkspaceAccessInformation], []),
        description="The access information of the workspace",
    )


class WorkspaceCluster(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: WorkspaceClusterStatus = Field(..., description="The status of the cluster")


class AvailableClusterResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    node_name: StrictStr = Field(..., description="The name of the node")
    node_endpoint: Optional[StrictStr] = Field(
        None, description="The endpoint of the node"
    )
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: WorkspaceGPUVendor = Field(..., description="The vendor of the GPU")
    gpu_count: int = Field(..., description="The count of the GPU")
    cpu_cores: int = Field(..., description="The count of the CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")


class WorkspaceTemplate(BaseModel):
    id_name: StrictStr = Field(..., description="The name of the workspace template")
    variables: Dict[str, Any] = Field(
        ..., description="The variables of the workspace template"
    )

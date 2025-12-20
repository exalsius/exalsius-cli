from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr

########################################################
# Cluster Domain Object
########################################################


class ClusterNodeResources(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The count of the CPU cores")
    memory_gb: StrictInt = Field(..., description="The amount of memory in GB")
    storage_gb: StrictInt = Field(..., description="The amount of storage in GB")


class ClusterNodeStatus(StrEnum):
    DISCOVERING = "DISCOVERING"
    AVAILABLE = "AVAILABLE"
    ADDED = "ADDED"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterNodeStatus:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterNodeRole(StrEnum):
    WORKER = "WORKER"
    CONTROL_PLANE = "CONTROL_PLANE"
    UNASSIGNED = "UNASSIGNED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterNodeRole:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterNode(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    role: ClusterNodeRole = Field(..., description="The role of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key of the node")
    status: ClusterNodeStatus = Field(..., description="The status of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    free_resources: ClusterNodeResources = Field(
        ..., description="The free resources of the node"
    )
    occupied_resources: ClusterNodeResources = Field(
        ..., description="The occupied resources of the node"
    )


class ClusterType(StrEnum):
    REMOTE = "REMOTE"
    ADOPTED = "ADOPTED"
    CLOUD = "CLOUD"
    DOCKER = "DOCKER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterType:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterStatus(StrEnum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    READY = "READY"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class Cluster(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: ClusterStatus = Field(..., description="The status of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    created_at: datetime = Field(..., description="The creation date of the cluster")
    updated_at: Optional[datetime] = Field(
        ..., description="The last update date of the cluster"
    )
    nodes: List[ClusterNode] = Field(..., description="The nodes of the cluster")

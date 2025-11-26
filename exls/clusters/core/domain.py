from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional, cast

from pydantic import BaseModel, Field, StrictInt, StrictStr


class ClusterType(StrEnum):
    REMOTE = "REMOTE"
    ADOPTED = "ADOPTED"
    CLOUD = "CLOUD"
    DOCKER = "DOCKER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterType:
        try:
            return cls(value)
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


class ClusterLabels(StrEnum):
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"
    TELEMETRY_TYPE = "cluster.exalsius.ai/telemetry-enabled"


class ClusterLabelValuesWorkloadType(StrEnum):
    VOLCANO = "volcano"


class Cluster(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: ClusterStatus = Field(..., description="The status of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    created_at: datetime = Field(..., description="The creation date of the cluster")
    updated_at: Optional[datetime] = Field(
        ..., description="The last update date of the cluster"
    )


class Resources(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The count of the CPU cores")
    memory_gb: StrictInt = Field(..., description="The amount of memory in GB")
    storage_gb: StrictInt = Field(..., description="The amount of storage in GB")


class ClusterNodeRefResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class ClusterNodeResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key: StrictStr = Field(..., description="The SSH key of the node")
    status: NodeStatus = Field(..., description="The status of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class NodeStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DISCOVERING = "DISCOVERING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> NodeStatus:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterNodeRole(StrEnum):
    WORKER = "WORKER"
    CONTROL_PLANE = "CONTROL_PLANE"


class ClustersNode(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key: StrictStr = Field(..., description="The SSH key of the node")
    status: NodeStatus = Field(..., description="The status of the node")
    role: ClusterNodeRole = Field(..., description="The role of the node")


class NodeValidationIssue(BaseModel):
    node_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the node, if known"
    )
    node_spec_repr: Optional[StrictStr] = Field(
        default=None, description="String representation of node spec if ID not known"
    )
    reason: StrictStr = Field(..., description="The reason for validation failure")


class DeployClusterResult(BaseModel):
    cluster: Optional[Cluster] = Field(default=None, description="The created cluster")
    issues: List[NodeValidationIssue] = Field(
        default_factory=lambda: cast(List[NodeValidationIssue], []),
        description="List of validation issues encountered",
    )

    @property
    def is_success(self) -> bool:
        return self.cluster is not None and len(self.issues) == 0


class NodesLoadingIssue(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    reason: StrictStr = Field(..., description="The reason for loading failure")


class NodesLoadingResult(BaseModel):
    nodes: List[ClustersNode] = Field(..., description="The loaded nodes")
    issues: Optional[List[NodesLoadingIssue]] = Field(
        default=None, description="List of loading issues encountered"
    )

    @property
    def is_success(self) -> bool:
        return self.issues is None or len(self.issues) == 0

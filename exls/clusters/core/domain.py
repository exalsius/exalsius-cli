from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr


class ClusterNodeRole(StrEnum):
    WORKER = "WORKER"
    CONTROL_PLANE = "CONTROL_PLANE"


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


class ClusterCreateType(StrEnum):
    REMOTE = "REMOTE"


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
    GPU_TYPE = "cluster.exalsius.ai/gpu-type"
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"
    TELEMETRY_TYPE = "cluster.exalsius.ai/telemetry-enabled"


class ClusterLabelValuesGPUType(StrEnum):
    NVIDIA = "nvidia"
    AMD = "amd"
    NO_GPU = "no-gpu"


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


class ClusterFilterCriteria(BaseModel):
    status: Optional[ClusterStatus] = Field(
        ..., description="The status of the cluster"
    )


class ClusterCreateRequest(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster")
    cluster_type: ClusterCreateType = Field(..., description="The type of the cluster")
    cluster_labels: Dict[StrictStr, StrictStr] = Field(
        ..., description="The labels of the cluster"
    )
    colony_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    worker_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the worker nodes"
    )


class NodeRef(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    role: ClusterNodeRole = Field(..., description="The role of the node")


class AddNodesRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_add: List[NodeRef] = Field(
        ..., description="The nodes to add to the cluster"
    )


class RemoveNodesRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_remove: List[NodeRef] = Field(
        ..., description="The nodes to remove from the cluster"
    )


class Resources(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The count of the CPU cores")
    memory_gb: StrictInt = Field(..., description="The amount of memory in GB")
    storage_gb: StrictInt = Field(..., description="The amount of storage in GB")


class ClusterNodeResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )

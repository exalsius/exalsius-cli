from __future__ import annotations

from datetime import datetime
from enum import Enum, StrEnum
from typing import Dict, List, Optional

from exalsius_api_client.models.cluster import Cluster as SdkCluster
from exalsius_api_client.models.hardware import Hardware as SdkResourcePool
from pydantic import BaseModel, Field, StrictInt, StrictStr

from exls.clusters.dtos import CreateClusterRequestDTO


class ClusterType(str, Enum):
    CLOUD = "CLOUD"
    REMOTE = "REMOTE"
    ADOPTED = "ADOPTED"
    DOCKER = "DOCKER"


class ClusterStatus(StrEnum):
    CREATING = "CREATING"
    CREATED = "CREATED"
    DELETING = "DELETING"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    UNKNOWN = "UNKNOWN"


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


class ClusterLabelValuesTelemetryType(StrEnum):
    ENABLED = "true"
    DISABLED = "false"


class ClusterNodeRole(StrEnum):
    WORKER = "WORKER"
    CONTROL_PLANE = "CONTROL_PLANE"


class ClusterFilterParams(BaseModel):
    status: Optional[ClusterStatus] = Field(
        default=None, description="The status of the cluster"
    )


class ClusterCreateParams(BaseModel):
    name: str = Field(..., description="The name of the cluster")
    cluster_type: ClusterType = Field(..., description="The type of the cluster")
    cluster_labels: Dict[str, str] = Field(..., description="The labels of the cluster")
    colony_id: Optional[str] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    k8s_version: Optional[str] = Field(
        default=None, description="The Kubernetes version of the cluster"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    control_plane_node_ids: Optional[List[str]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    worker_node_ids: Optional[List[str]] = Field(
        default=None, description="The IDs of the worker nodes"
    )

    @classmethod
    def from_request_dto(
        cls, request_dto: CreateClusterRequestDTO
    ) -> ClusterCreateParams:
        gpu_type_enum: ClusterLabelValuesGPUType = ClusterLabelValuesGPUType(
            request_dto.gpu_type
        )
        cluster_labels: Dict[str, str] = {}
        if gpu_type_enum != ClusterLabelValuesGPUType.NO_GPU:
            cluster_labels[ClusterLabels.GPU_TYPE] = gpu_type_enum.value
        if request_dto.diloco:
            cluster_labels[ClusterLabels.WORKLOAD_TYPE] = (
                ClusterLabelValuesWorkloadType.VOLCANO
            )
        if request_dto.telemetry_enabled:
            cluster_labels[ClusterLabels.TELEMETRY_TYPE] = (
                ClusterLabelValuesTelemetryType.ENABLED
            )
        return cls(
            name=request_dto.name,
            cluster_type=request_dto.cluster_type,
            cluster_labels=cluster_labels,
        )


class NodeToAddParams(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node to add")
    node_role: ClusterNodeRole = Field(..., description="The role of the node to add")


class AddNodesParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_add: List[NodeToAddParams] = Field(
        ..., description="The nodes to add to the cluster"
    )


class RemoveNodeParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    node_id: StrictStr = Field(..., description="The ID of the node to remove")


class Cluster(BaseModel):
    sdk_model: SdkCluster = Field(..., description="The SDK model of the cluster")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def name(self) -> StrictStr:
        return self.sdk_model.name

    @property
    def cluster_status(self) -> ClusterStatus:
        return ClusterStatus(self.sdk_model.cluster_status)

    @property
    def created_at(self) -> datetime:
        return self.sdk_model.created_at

    @property
    def updated_at(self) -> Optional[datetime]:
        return self.sdk_model.updated_at


class Resources(BaseModel):
    sdk_model: SdkResourcePool = Field(
        ..., description="The SDK model of the resources"
    )

    @property
    def gpu_type(self) -> Optional[StrictStr]:
        return self.sdk_model.gpu_type

    @property
    def gpu_vendor(self) -> Optional[StrictStr]:
        return self.sdk_model.gpu_vendor

    @property
    def gpu_count(self) -> StrictInt:
        if self.sdk_model.gpu_count is None:
            return 0
        return self.sdk_model.gpu_count

    @property
    def cpu_cores(self) -> StrictInt:
        if self.sdk_model.cpu_cores is None:
            return 0
        return self.sdk_model.cpu_cores

    @property
    def memory_gb(self) -> StrictInt:
        if self.sdk_model.memory_gb is None:
            return 0
        return self.sdk_model.memory_gb

    @property
    def storage_gb(self) -> StrictInt:
        if self.sdk_model.storage_gb is None:
            return 0
        return self.sdk_model.storage_gb


class ClusterNodeResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class ClusterNodeRef(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    role: ClusterNodeRole = Field(..., description="The role of the node")

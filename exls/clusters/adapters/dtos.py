from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr


class AllowedClusterStatusDTO(StrEnum):
    CREATED = "pending"
    DEPLOYING = "deploying"
    READY = "ready"
    FAILED = "failed"


class AllowedGpuTypesDTO(StrEnum):
    NVIDIA = "nvidia"
    AMD = "amd"
    NO_GPU = "no-gpu"

    @classmethod
    def values(cls) -> List[AllowedGpuTypesDTO]:
        return list(cls.__members__.values())


class AllowedClusterNodeRoleDTO(StrEnum):
    WORKER = "worker"
    CONTROL_PLANE = "control-plane"


class AllowedClusterTypesDTO(StrEnum):
    # CLOUD = "cloud"
    REMOTE = "remote"
    # ADOPTED = "adopted"

    @classmethod
    def values(cls) -> List[AllowedClusterTypesDTO]:
        return list(cls.__members__.values())


class AddNodesRequestDTO(BaseModel):
    cluster_id: StrictStr = Field(
        ..., description="The ID of the cluster to add nodes to"
    )
    node_ids: List[StrictStr] = Field(..., description="The IDs of the nodes to add")
    node_role: AllowedClusterNodeRoleDTO = Field(
        ..., description="The role of the nodes to add"
    )


class RemoveNodeRequestDTO(BaseModel):
    cluster_id: StrictStr = Field(
        ..., description="The ID of the cluster to remove a node from"
    )
    node_id: StrictStr = Field(..., description="The ID of the node to remove")


class ClusterDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: StrictStr = Field(..., description="The status of the cluster")
    type: StrictStr = Field(..., description="The type of the cluster")
    created_at: datetime = Field(..., description="The creation date of the cluster")
    updated_at: Optional[datetime] = Field(
        default=None, description="The last update date of the cluster"
    )


class ClusterWithNodesDTO(ClusterDTO):
    worker_nodes: List[ClusterNodeDTO] = Field(
        ..., description="The worker nodes of the cluster"
    )
    control_plane_nodes: List[ClusterNodeDTO] = Field(
        ..., description="The control plane nodes of the cluster"
    )


class ClusterNodeDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    role: StrictStr = Field(..., description="The role of the nodes")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    status: StrictStr = Field(..., description="The status of the node")
    cluster_name: StrictStr = Field(..., description="The name of the cluster")


class ResourcesDTO(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The CPU of the resources")
    memory_gb: StrictInt = Field(..., description="The memory of the resources")
    storage_gb: StrictInt = Field(..., description="The storage of the resources")


class ClusterNodeResourcesDTO(BaseModel):
    cluster_node: ClusterNodeDTO = Field(..., description="The cluster node")
    free_resources: ResourcesDTO = Field(
        ..., description="The free resources of the node"
    )
    occupied_resources: ResourcesDTO = Field(
        ..., description="The occupied resources of the node"
    )


class DashboardUrlResponseDTO(BaseModel):
    url: StrictStr = Field(..., description="The dashboard URL")


class NodeValidationIssueDTO(BaseModel):
    node_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the node, if known"
    )
    node_spec_repr: Optional[StrictStr] = Field(
        default=None, description="String representation of node spec if ID not known"
    )
    reason: StrictStr = Field(..., description="The reason for validation failure")

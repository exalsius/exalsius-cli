from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr

from exls.clusters.domain import (
    Cluster,
    ClusterNodeRef,
    ClusterNodeResources,
    Resources,
)
from exls.nodes.domain import BaseNode


class AllowedClusterStatusDTO(StrEnum):
    CREATING = "creating"
    CREATED = "created"
    DELETING = "deleting"
    FAILED = "failed"
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


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


class ListClustersRequestDTO(BaseModel):
    status: Optional[AllowedClusterStatusDTO] = Field(
        default=None, description="The status of the cluster"
    )


class DeployClusterRequestDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster")
    cluster_type: AllowedClusterTypesDTO = Field(
        ..., description="The type of the cluster"
    )
    gpu_type: AllowedGpuTypesDTO = Field(..., description="The type of the GPU")
    worker_node_ids: List[StrictStr] = Field(
        ..., description="The IDs of the worker nodes"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    enable_multinode_training: bool = Field(
        ...,
        description="Enable multinode AI model training for the cluster",
    )
    enable_telemetry: bool = Field(..., description="Enable telemetry for the cluster")


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
    id: StrictStr
    name: StrictStr
    cluster_status: StrictStr
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_domain(cls, domain_obj: Cluster) -> ClusterDTO:
        return cls(
            id=domain_obj.id,
            name=domain_obj.name,
            cluster_status=domain_obj.cluster_status,
            created_at=domain_obj.created_at,
            updated_at=domain_obj.updated_at,
        )


class ClusterNodeDTO(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    cluster_name: StrictStr = Field(..., description="The name of the cluster")
    node_id: StrictStr = Field(..., description="The ID of the node")
    node_role: StrictStr = Field(..., description="The role of the nodes")
    node_hostname: StrictStr = Field(..., description="The hostname of the node")
    node_status: StrictStr = Field(..., description="The status of the node")

    @classmethod
    def from_domain(
        cls,
        cluster: Cluster,
        cluster_node_ref: ClusterNodeRef,
        node: BaseNode,
    ) -> ClusterNodeDTO:
        return cls(
            cluster_id=cluster.id,
            cluster_name=cluster.name,
            node_id=cluster_node_ref.node_id,
            node_role=cluster_node_ref.role,
            node_hostname=node.hostname or "",
            node_status=node.node_status,
        )


class ResourcesDTO(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu: StrictInt = Field(..., description="The CPU of the resources")
    memory: StrictInt = Field(..., description="The memory of the resources")
    storage: StrictInt = Field(..., description="The storage of the resources")

    @classmethod
    def from_domain(cls, resources: Resources) -> ResourcesDTO:
        return cls(
            gpu_type=resources.gpu_type or "N/A",
            gpu_vendor=resources.gpu_vendor or "N/A",
            gpu_count=resources.gpu_count,
            cpu=resources.cpu_cores,
            memory=resources.memory_gb,
            storage=resources.storage_gb,
        )


class ClusterNodeResourcesDTO(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    free_resources: ResourcesDTO = Field(
        ..., description="The free resources of the node"
    )
    occupied_resources: ResourcesDTO = Field(
        ..., description="The occupied resources of the node"
    )

    @classmethod
    def from_resources(
        cls,
        cluster_node_resources: ClusterNodeResources,
    ) -> ClusterNodeResourcesDTO:
        return cls(
            node_id=cluster_node_resources.node_id,
            free_resources=ResourcesDTO.from_domain(
                cluster_node_resources.free_resources
            ),
            occupied_resources=ResourcesDTO.from_domain(
                cluster_node_resources.occupied_resources
            ),
        )


class DashboardUrlResponseDTO(BaseModel):
    url: StrictStr = Field(..., description="The dashboard URL")

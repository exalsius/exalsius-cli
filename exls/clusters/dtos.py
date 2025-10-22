from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr

from exls.clusters.domain import (
    Cluster,
    ClusterNodeRef,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterStatus,
    ClusterType,
    Resources,
)
from exls.nodes.domain import BaseNode


class GpuTypeDTO(str, Enum):
    NVIDIA = "nvidia"
    AMD = "amd"
    NO_GPU = "no-gpu"


class ListClustersRequestDTO(BaseModel):
    status: Optional[ClusterStatus] = Field(
        default=None, description="The status of the cluster"
    )


class ClusterDTO(BaseModel):
    id: StrictStr
    name: StrictStr
    cluster_status: ClusterStatus
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


class CreateClusterRequestDTO(BaseModel):
    name: str = Field(..., description="The name of the cluster")
    cluster_type: ClusterType = Field(..., description="The type of the cluster")
    gpu_type: GpuTypeDTO = Field(
        default=GpuTypeDTO.NVIDIA, description="The type of the GPU"
    )
    diloco: bool = Field(
        False,
        description="Add the volcano workload type to the cluster to support Diloco workloads",
    )
    telemetry_enabled: bool = Field(
        False, description="Enable telemetry for the cluster"
    )


class AddNodesRequestDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster to add nodes to")
    node_ids: List[str] = Field(..., description="The IDs of the nodes to add")
    node_role: ClusterNodeRole = Field(..., description="The role of the nodes to add")


class ClusterNodeDTO(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    cluster_name: StrictStr = Field(..., description="The name of the cluster")
    node_id: StrictStr = Field(..., description="The ID of the node")
    node_role: ClusterNodeRole = Field(..., description="The role of the nodes")
    node_hostname: StrictStr = Field(..., description="The hostname of the node")

    @classmethod
    def from_domain(
        cls,
        cluster_id: str,
        cluster_name: str,
        cluster_node_ref: ClusterNodeRef,
        node: BaseNode,
    ) -> ClusterNodeDTO:
        return cls(
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            node_id=cluster_node_ref.node_id,
            node_role=cluster_node_ref.role,
            node_hostname=node.hostname or "",
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


class ClusterNodeResourcesDTO(ClusterNodeDTO):
    free_resources: ResourcesDTO = Field(
        ..., description="The free resources of the node"
    )
    occupied_resources: ResourcesDTO = Field(
        ..., description="The occupied resources of the node"
    )

    @classmethod
    def from_base_dto(
        cls,
        base_dto: ClusterNodeDTO,
        cluster_node_resources: ClusterNodeResources,
    ) -> ClusterNodeResourcesDTO:
        return cls(
            **base_dto.model_dump(),
            free_resources=ResourcesDTO.from_domain(
                cluster_node_resources.free_resources
            ),
            occupied_resources=ResourcesDTO.from_domain(
                cluster_node_resources.occupied_resources
            ),
        )

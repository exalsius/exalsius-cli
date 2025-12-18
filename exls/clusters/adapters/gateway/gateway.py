import datetime
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr

from exls.clusters.core.domain import (
    ClusterStatus,
)

# It's a leaky abstraction between the domain and the gateway layer.
# Strong abstraction is not needed here for now.
from exls.clusters.core.ports.repository import ClusterCreateParameters


class ClusterData(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: StrictStr = Field(..., description="The status of the cluster")
    type: StrictStr = Field(..., description="The type of the cluster")
    created_at: datetime.datetime = Field(
        ..., description="The creation date of the cluster"
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="The last update date of the cluster"
    )


class ClusterNodeRefData(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    role: StrictStr = Field(..., description="The role of the node")


class ResourcesData(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The number of CPU cores")
    memory_gb: StrictInt = Field(..., description="The amount of memory in GB")
    storage_gb: StrictInt = Field(..., description="The amount of storage in GB")


class ClusterNodeRefResourcesData(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    node_name: StrictStr = Field(..., description="The name of the node")
    free_resources: ResourcesData = Field(
        ..., description="The free resources of the node"
    )
    occupied_resources: ResourcesData = Field(
        ..., description="The occupied resources of the node"
    )


class _ClusterLabels(StrEnum):
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"


class _ClusterLabelValuesWorkloadType(StrEnum):
    VOLCANO = "volcano"


def get_cluster_labels(
    parameters: ClusterCreateParameters,
) -> Dict[StrictStr, StrictStr]:
    labels: Dict[StrictStr, StrictStr] = {}
    if parameters.enable_multinode_training:
        labels[_ClusterLabels.WORKLOAD_TYPE] = _ClusterLabelValuesWorkloadType.VOLCANO
    return labels


class ClustersGateway(ABC):
    @abstractmethod
    def list(self, status: Optional[ClusterStatus]) -> List[ClusterData]:
        raise NotImplementedError

    @abstractmethod
    def get(self, cluster_id: str) -> ClusterData:
        raise NotImplementedError

    @abstractmethod
    def delete(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create(self, parameters: ClusterCreateParameters) -> str:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeRefData]:
        raise NotImplementedError

    @abstractmethod
    def get_cluster_resources(
        self, cluster_id: str
    ) -> List[ClusterNodeRefResourcesData]:
        raise NotImplementedError

    @abstractmethod
    def add_nodes_to_cluster(
        self, cluster_id: str, nodes_to_add: List[ClusterNodeRefData]
    ) -> List[ClusterNodeRefData]:
        raise NotImplementedError

    @abstractmethod
    def remove_node_from_cluster(self, cluster_id: str, node_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def load_kubeconfig(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_dashboard_url(self, cluster_id: str) -> str:
        raise NotImplementedError

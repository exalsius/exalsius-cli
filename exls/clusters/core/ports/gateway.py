from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import (
    Cluster,
    ClusterStatus,
    ClusterType,
    Resources,
)
from exls.clusters.core.requests import AddNodesRequest, NodeRef


class ClusterLabels(StrEnum):
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"


class ClusterLabelValuesWorkloadType(StrEnum):
    VOLCANO = "volcano"


class ClusterCreateParameters(BaseModel):
    """Domain object representing parameters for creating a cluster."""

    name: StrictStr = Field(..., description="The name of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    vpn_cluster: bool = Field(..., description="Whether the cluster is a VPN cluster")
    telemetry_enabled: bool = Field(
        ..., description="Whether telemetry is enabled for the cluster"
    )
    labels: Dict[StrictStr, StrictStr] = Field(
        ..., description="The labels of the cluster"
    )
    colony_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    worker_node_ids: List[StrictStr] = Field(
        ..., description="The IDs of the worker nodes"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )

    @classmethod
    def get_labels(cls, enable_multinode_training: bool) -> Dict[StrictStr, StrictStr]:
        labels: Dict[StrictStr, StrictStr] = {}
        if enable_multinode_training:
            labels[ClusterLabels.WORKLOAD_TYPE] = ClusterLabelValuesWorkloadType.VOLCANO
        return labels


class ClusterNodeRefResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class IClustersGateway(ABC):
    @abstractmethod
    def list(self, status: Optional[ClusterStatus]) -> List[Cluster]:
        raise NotImplementedError

    @abstractmethod
    def get(self, cluster_id: str) -> Cluster:
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
    def get_cluster_nodes(self, cluster_id: str) -> List[NodeRef]:
        raise NotImplementedError

    @abstractmethod
    def add_nodes_to_cluster(self, request: AddNodesRequest) -> List[NodeRef]:
        raise NotImplementedError

    @abstractmethod
    def remove_nodes_from_cluster(
        self, cluster_id: str, node_ids: List[StrictStr]
    ) -> List[StrictStr]:
        raise NotImplementedError

    @abstractmethod
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeRefResources]:
        raise NotImplementedError

    @abstractmethod
    def get_kubeconfig(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_dashboard_url(self, cluster_id: str) -> str:
        raise NotImplementedError

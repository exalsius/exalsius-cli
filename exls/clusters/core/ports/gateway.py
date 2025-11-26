from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import (
    Cluster,
    ClusterNodeRefResources,
    ClusterStatus,
    ClusterType,
)
from exls.clusters.core.requests import (
    AddNodesRequest,
    NodeRef,
    RemoveNodesRequest,
)


class ClusterCreateParameters(BaseModel):
    """Domain object representing parameters for creating a cluster."""

    name: StrictStr = Field(..., description="The name of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
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
    def remove_nodes_from_cluster(self, request: RemoveNodesRequest) -> List[str]:
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

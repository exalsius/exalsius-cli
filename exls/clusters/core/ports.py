from abc import ABC, abstractmethod
from typing import List

from exls.clusters.core.domain import (
    AddNodesRequest,
    Cluster,
    ClusterCreateRequest,
    ClusterFilterCriteria,
    ClusterNodeResources,
    NodeRef,
    RemoveNodesRequest,
)


class IClustersGateway(ABC):
    @abstractmethod
    def list(self, criteria: ClusterFilterCriteria) -> List[Cluster]:
        raise NotImplementedError

    @abstractmethod
    def get(self, cluster_id: str) -> Cluster:
        raise NotImplementedError

    @abstractmethod
    def delete(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create(self, request: ClusterCreateRequest) -> str:
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
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        raise NotImplementedError

    @abstractmethod
    def get_kubeconfig(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_dashboard_url(self, cluster_id: str) -> str:
        raise NotImplementedError

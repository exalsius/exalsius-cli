from abc import ABC, abstractmethod
from typing import List

from exalsius.clusters.domain import (
    AddNodesParams,
    Cluster,
    ClusterCreateParams,
    ClusterFilterParams,
    ClusterNodeRef,
    ClusterNodeResources,
    RemoveNodeParams,
)


class ClustersGateway(ABC):
    @abstractmethod
    def list(self, cluster_filter_params: ClusterFilterParams) -> List[Cluster]:
        raise NotImplementedError

    @abstractmethod
    def get(self, cluster_id: str) -> Cluster:
        raise NotImplementedError

    @abstractmethod
    def delete(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create(self, cluster_create_params: ClusterCreateParams) -> str:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, cluster_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeRef]:
        raise NotImplementedError

    @abstractmethod
    def add_nodes_to_cluster(
        self, add_nodes_params: AddNodesParams
    ) -> List[ClusterNodeRef]:
        raise NotImplementedError

    @abstractmethod
    def remove_node_from_cluster(self, remove_node_params: RemoveNodeParams) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        raise NotImplementedError

    @abstractmethod
    def get_kubeconfig(self, cluster_id: str) -> str:
        raise NotImplementedError

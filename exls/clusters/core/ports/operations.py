from abc import ABC, abstractmethod
from typing import List

from exls.clusters.core.domain import ClusterNode
from exls.clusters.core.results import ClusterScaleResult


class ClusterOperations(ABC):
    @abstractmethod
    def deploy(self, cluster_id: str) -> str: ...

    @abstractmethod
    def scale_up(
        self, cluster_id: str, nodes_to_add: List[ClusterNode]
    ) -> ClusterScaleResult: ...

    @abstractmethod
    def scale_down(
        self, cluster_id: str, nodes_to_remove: List[ClusterNode]
    ) -> ClusterScaleResult: ...

    @abstractmethod
    def load_kubeconfig(self, cluster_id: str) -> str: ...

    @abstractmethod
    def get_dashboard_url(self, cluster_id: str) -> str: ...

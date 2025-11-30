from abc import ABC, abstractmethod
from typing import List

from exls.workspaces.core.domain import (
    AvailableClusterResources,
    WorkspaceCluster,
    WorkspaceTemplate,
)


class IClustersProvider(ABC):
    @abstractmethod
    def list_clusters(self) -> List[WorkspaceCluster]: ...

    @abstractmethod
    def get_cluster(self, cluster_id: str) -> WorkspaceCluster: ...

    @abstractmethod
    def get_cluster_resources(
        self, cluster_id: str
    ) -> List[AvailableClusterResources]: ...


class IWorkspaceTemplatesProvider(ABC):
    @abstractmethod
    def list_workspace_templates(self) -> List[WorkspaceTemplate]: ...

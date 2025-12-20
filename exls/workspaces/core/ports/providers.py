from abc import ABC, abstractmethod
from typing import List

from exls.workspaces.core.domain import (
    WorkspaceCluster,
    WorkspaceTemplate,
)


class ClustersProvider(ABC):
    @abstractmethod
    def list_clusters(self) -> List[WorkspaceCluster]: ...

    @abstractmethod
    def get_cluster(self, cluster_id: str) -> WorkspaceCluster: ...


class WorkspaceTemplatesProvider(ABC):
    @abstractmethod
    def list_workspace_templates(self) -> List[WorkspaceTemplate]: ...

from abc import ABC, abstractmethod
from typing import List, Optional

from exls.workspaces.core.domain import Workspace


class WorkspaceRepository(ABC):
    @abstractmethod
    def list(self, cluster_id: Optional[str] = None) -> List[Workspace]:
        raise NotImplementedError

    @abstractmethod
    def get(self, workspace_id: str) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    def delete(self, workspace_id: str) -> str:
        raise NotImplementedError

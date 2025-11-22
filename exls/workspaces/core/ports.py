from abc import ABC, abstractmethod
from typing import List

from exls.workspaces.core.domain import DeployWorkspaceRequest, Workspace


class IWorkspacesGateway(ABC):
    @abstractmethod
    def list(self, cluster_id: str) -> List[Workspace]:
        raise NotImplementedError

    @abstractmethod
    def get(self, workspace_id: str) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, request: DeployWorkspaceRequest) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete(self, workspace_id: str) -> str:
        raise NotImplementedError

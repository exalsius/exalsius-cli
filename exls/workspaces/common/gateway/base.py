from abc import ABC, abstractmethod
from typing import List

from exls.workspaces.common.domain import (
    Workspace,
)
from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


class WorkspacesGateway(ABC):
    @abstractmethod
    def list(self, cluster_id: str) -> List[Workspace]:
        raise NotImplementedError

    @abstractmethod
    def get(self, workspace_id: str) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, deploy_params: DeployWorkspaceParams) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete(self, workspace_id: str) -> str:
        raise NotImplementedError

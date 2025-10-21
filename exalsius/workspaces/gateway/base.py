from abc import ABC, abstractmethod
from typing import List

from exalsius.workspaces.domain import (
    DeployWorkspaceParams,
    Workspace,
    WorkspaceFilterParams,
)


class WorkspacesGateway(ABC):
    @abstractmethod
    def list(self, workspace_filter_params: WorkspaceFilterParams) -> List[Workspace]:
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

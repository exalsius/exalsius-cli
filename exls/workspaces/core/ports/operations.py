from abc import ABC, abstractmethod

from exls.workspaces.core.requests import DeployWorkspaceRequest


class WorkspaceOperations(ABC):
    # We leake the domain's request here, which is fine since they
    # are identical
    @abstractmethod
    def deploy(self, parameters: DeployWorkspaceRequest) -> str:
        raise NotImplementedError

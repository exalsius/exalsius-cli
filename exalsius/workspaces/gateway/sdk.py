from typing import List

from exalsius_api_client.api.workspaces_api import WorkspacesApi

from exalsius.workspaces.domain import (
    DeployWorkspaceParams,
    Workspace,
    WorkspaceFilterParams,
)
from exalsius.workspaces.gateway.base import WorkspacesGateway
from exalsius.workspaces.gateway.commands import (
    DeleteWorkspaceSdkCommand,
    DeployWorkspaceSdkCommand,
    GetWorkspaceSdkCommand,
    ListWorkspacesSdkCommand,
)


class WorkspacesGatewaySdk(WorkspacesGateway):
    def __init__(self, workspaces_api: WorkspacesApi):
        self._workspaces_api = workspaces_api

    def list(self, workspace_filter_params: WorkspaceFilterParams) -> List[Workspace]:
        command: ListWorkspacesSdkCommand = ListWorkspacesSdkCommand(
            self._workspaces_api, params=workspace_filter_params
        )
        return command.execute()

    def get(self, workspace_id: str) -> Workspace:
        command: GetWorkspaceSdkCommand = GetWorkspaceSdkCommand(
            self._workspaces_api, params=workspace_id
        )
        return command.execute()

    def deploy(self, deploy_params: DeployWorkspaceParams) -> str:
        command: DeployWorkspaceSdkCommand = DeployWorkspaceSdkCommand(
            self._workspaces_api, params=deploy_params
        )
        return command.execute()

    def delete(self, workspace_id: str) -> str:
        command: DeleteWorkspaceSdkCommand = DeleteWorkspaceSdkCommand(
            self._workspaces_api, params=workspace_id
        )
        return command.execute()

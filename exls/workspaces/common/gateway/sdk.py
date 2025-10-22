from typing import List

from exalsius_api_client.api.workspaces_api import WorkspacesApi

from exls.workspaces.common.domain import (
    DeployWorkspaceParams,
    Workspace,
    WorkspaceFilterParams,
)
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.gateway.commands import (
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

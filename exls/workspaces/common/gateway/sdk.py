from typing import List, Union

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace import Workspace as SdkWorkspace
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.common.domain import (
    Workspace,
)
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.gateway.commands import (
    DeleteWorkspaceSdkCommand,
    DeployWorkspaceSdkCommand,
    GetWorkspaceSdkCommand,
    ListWorkspacesSdkCommand,
)
from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams
from exls.workspaces.common.gateway.mappers import to_create_request


class WorkspacesGatewaySdk(WorkspacesGateway):
    def __init__(self, workspaces_api: WorkspacesApi):
        self._workspaces_api = workspaces_api

    def _create_from_sdk_model(self, sdk_model: SdkWorkspace) -> Workspace:
        return Workspace(sdk_model=sdk_model)

    def list(self, cluster_id: str) -> List[Workspace]:
        command: ListWorkspacesSdkCommand = ListWorkspacesSdkCommand(
            self._workspaces_api, params=cluster_id
        )
        response: WorkspacesListResponse = command.execute()
        return [
            self._create_from_sdk_model(sdk_model=workspace)
            for workspace in response.workspaces
        ]

    def get(self, workspace_id: str) -> Workspace:
        command: GetWorkspaceSdkCommand = GetWorkspaceSdkCommand(
            self._workspaces_api, params=workspace_id
        )
        response: WorkspaceResponse = command.execute()
        return self._create_from_sdk_model(sdk_model=response.workspace)

    def deploy(
        self, deploy_params: Union[DeployWorkspaceParams, WorkspaceDeployConfigDTO]
    ) -> str:
        """Deploy a workspace. Accepts DeployWorkspaceParams or WorkspaceDeployConfigDTO."""
        request: WorkspaceCreateRequest = to_create_request(deploy_params)
        command: DeployWorkspaceSdkCommand = DeployWorkspaceSdkCommand(
            self._workspaces_api, params=request
        )
        response: WorkspaceCreateResponse = command.execute()
        return response.workspace_id

    def delete(self, workspace_id: str) -> str:
        command: DeleteWorkspaceSdkCommand = DeleteWorkspaceSdkCommand(
            self._workspaces_api, params=workspace_id
        )
        response: WorkspaceDeleteResponse = command.execute()
        return response.workspace_id

from typing import List

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.shared.adapters.gateway.sdk.service import create_api_client
from exls.workspaces.adapters.gateway.commands import (
    DeleteWorkspaceSdkCommand,
    DeployWorkspaceSdkCommand,
    GetWorkspaceSdkCommand,
    ListWorkspacesSdkCommand,
)
from exls.workspaces.adapters.gateway.mappers import (
    deploy_workspace_request_to_create_request,
    workspace_from_sdk,
)
from exls.workspaces.core.domain import (
    DeployWorkspaceRequest,
    Workspace,
)
from exls.workspaces.core.ports import IWorkspacesGateway


class WorkspacesGatewaySdk(IWorkspacesGateway):
    def __init__(self, workspaces_api: WorkspacesApi):
        self._workspaces_api = workspaces_api

    def list(self, cluster_id: str) -> List[Workspace]:
        command: ListWorkspacesSdkCommand = ListWorkspacesSdkCommand(
            self._workspaces_api, cluster_id=cluster_id
        )
        response: WorkspacesListResponse = command.execute()
        return [
            workspace_from_sdk(sdk_model=workspace) for workspace in response.workspaces
        ]

    def get(self, workspace_id: str) -> Workspace:
        command: GetWorkspaceSdkCommand = GetWorkspaceSdkCommand(
            self._workspaces_api, workspace_id=workspace_id
        )
        response: WorkspaceResponse = command.execute()
        return workspace_from_sdk(sdk_model=response.workspace)

    def deploy(self, request: DeployWorkspaceRequest) -> str:
        """Deploy a workspace."""
        create_request: WorkspaceCreateRequest = (
            deploy_workspace_request_to_create_request(request=request)
        )
        command: DeployWorkspaceSdkCommand = DeployWorkspaceSdkCommand(
            self._workspaces_api, request=create_request
        )
        response: WorkspaceCreateResponse = command.execute()
        return response.workspace_id

    def delete(self, workspace_id: str) -> str:
        command: DeleteWorkspaceSdkCommand = DeleteWorkspaceSdkCommand(
            self._workspaces_api, workspace_id=workspace_id
        )
        response: WorkspaceDeleteResponse = command.execute()
        return response.workspace_id


def create_workspaces_gateway(
    backend_host: str, access_token: str
) -> IWorkspacesGateway:
    workspaces_api: WorkspacesApi = WorkspacesApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return WorkspacesGatewaySdk(workspaces_api=workspaces_api)

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.shared.adapters.gateway.sdk.command import ExalsiusSdkCommand


class BaseWorkspacesSdkCommand[T_Cmd_Return](
    ExalsiusSdkCommand[WorkspacesApi, T_Cmd_Return]
):
    """Base class for all workspaces commands."""

    pass


class ListWorkspacesSdkCommand(BaseWorkspacesSdkCommand[WorkspacesListResponse]):
    def __init__(self, api_client: WorkspacesApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> WorkspacesListResponse:
        response: WorkspacesListResponse = self.api_client.list_workspaces(
            cluster_id=self._cluster_id
        )
        return response


class GetWorkspaceSdkCommand(BaseWorkspacesSdkCommand[WorkspaceResponse]):
    def __init__(self, api_client: WorkspacesApi, workspace_id: str):
        super().__init__(api_client)
        self._workspace_id: str = workspace_id

    def _execute_api_call(self) -> WorkspaceResponse:
        response: WorkspaceResponse = self.api_client.describe_workspace(
            workspace_id=self._workspace_id
        )
        return response


class DeployWorkspaceSdkCommand(BaseWorkspacesSdkCommand[WorkspaceCreateResponse]):
    def __init__(self, api_client: WorkspacesApi, request: WorkspaceCreateRequest):
        super().__init__(api_client)
        self._request: WorkspaceCreateRequest = request

    def _execute_api_call(self) -> WorkspaceCreateResponse:
        response: WorkspaceCreateResponse = self.api_client.create_workspace(
            workspace_create_request=self._request
        )
        return response


class DeleteWorkspaceSdkCommand(BaseWorkspacesSdkCommand[WorkspaceDeleteResponse]):
    def __init__(self, api_client: WorkspacesApi, workspace_id: str):
        super().__init__(api_client)
        self._workspace_id: str = workspace_id

    def _execute_api_call(self) -> WorkspaceDeleteResponse:
        response: WorkspaceDeleteResponse = self.api_client.delete_workspace(
            workspace_id=self._workspace_id
        )
        return response

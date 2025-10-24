from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.core.commons.gateways.commands.sdk import ExalsiusSdkCommand


class BaseWorkspacesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[WorkspacesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all workspaces commands."""

    pass


class ListWorkspacesSdkCommand(BaseWorkspacesSdkCommand[str, WorkspacesListResponse]):
    def _execute_api_call(self, params: Optional[str]) -> WorkspacesListResponse:
        assert params is not None
        response: WorkspacesListResponse = self.api_client.list_workspaces(
            cluster_id=params
        )
        return response


class GetWorkspaceSdkCommand(BaseWorkspacesSdkCommand[str, WorkspaceResponse]):
    def _execute_api_call(self, params: Optional[str]) -> WorkspaceResponse:
        assert params is not None
        response: WorkspaceResponse = self.api_client.describe_workspace(
            workspace_id=params
        )
        return response


class DeployWorkspaceSdkCommand(
    BaseWorkspacesSdkCommand[WorkspaceCreateRequest, WorkspaceCreateResponse]
):
    def _execute_api_call(
        self, params: Optional[WorkspaceCreateRequest]
    ) -> WorkspaceCreateResponse:
        assert params is not None
        response: WorkspaceCreateResponse = self.api_client.create_workspace(
            workspace_create_request=params
        )
        return response


class DeleteWorkspaceSdkCommand(BaseWorkspacesSdkCommand[str, WorkspaceDeleteResponse]):
    def _execute_api_call(self, params: Optional[str]) -> WorkspaceDeleteResponse:
        assert params is not None
        response: WorkspaceDeleteResponse = self.api_client.delete_workspace(
            workspace_id=params
        )
        return response

from typing import List, Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.core.commons.commands.sdk import ExalsiusSdkCommand
from exls.workspaces.common.domain import (
    DeployWorkspaceParams,
    Workspace,
    WorkspaceFilterParams,
)
from exls.workspaces.common.gateway.mappers import to_create_request


class BaseWorkspacesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[WorkspacesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all workspaces commands."""

    pass


class ListWorkspacesSdkCommand(
    BaseWorkspacesSdkCommand[WorkspaceFilterParams, List[Workspace]]
):
    def _execute_api_call(
        self, params: Optional[WorkspaceFilterParams]
    ) -> List[Workspace]:
        assert params is not None
        response: WorkspacesListResponse = self.api_client.list_workspaces(
            cluster_id=params.cluster_id
        )
        return [Workspace(sdk_model=workspace) for workspace in response.workspaces]


class GetWorkspaceSdkCommand(BaseWorkspacesSdkCommand[str, Workspace]):
    def _execute_api_call(self, params: Optional[str]) -> Workspace:
        assert params is not None
        response: WorkspaceResponse = self.api_client.describe_workspace(
            workspace_id=params
        )
        return Workspace(sdk_model=response.workspace)


class DeployWorkspaceSdkCommand(BaseWorkspacesSdkCommand[DeployWorkspaceParams, str]):
    def _execute_api_call(self, params: Optional[DeployWorkspaceParams]) -> str:
        assert params is not None
        request: WorkspaceCreateRequest = to_create_request(params=params)
        response: WorkspaceCreateResponse = self.api_client.create_workspace(
            workspace_create_request=request
        )
        return response.workspace_id


class DeleteWorkspaceSdkCommand(BaseWorkspacesSdkCommand[str, str]):
    def _execute_api_call(self, params: Optional[str]) -> str:
        assert params is not None
        response: WorkspaceDeleteResponse = self.api_client.delete_workspace(
            workspace_id=params
        )
        return response.workspace_id

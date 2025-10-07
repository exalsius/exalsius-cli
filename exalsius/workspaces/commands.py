from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.workspaces.models import (
    CreateWorkspaceRequestDTO,
    DeleteWorkspaceRequestDTO,
    GetWorkspaceRequestDTO,
    WorkspacesListRequestDTO,
)


class ListWorkspacesCommand(
    ExalsiusAPICommand[WorkspacesApi, WorkspacesListRequestDTO, WorkspacesListResponse]
):
    def _execute_api_call(self) -> WorkspacesListResponse:
        return self.api_client.list_workspaces(cluster_id=self.request.cluster_id)


class GetWorkspaceCommand(
    ExalsiusAPICommand[WorkspacesApi, GetWorkspaceRequestDTO, WorkspaceResponse]
):
    def _execute_api_call(self) -> WorkspaceResponse:
        return self.api_client.describe_workspace(
            workspace_id=self.request.workspace_id
        )


class CreateWorkspaceCommand(
    ExalsiusAPICommand[
        WorkspacesApi, CreateWorkspaceRequestDTO, WorkspaceCreateResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceCreateResponse:
        return self.api_client.create_workspace(self.request.to_api_model())


class CreateWorkspacePodCommand(
    ExalsiusAPICommand[
        WorkspacesApi, CreateWorkspaceRequestDTO, WorkspaceCreateResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceCreateResponse:
        return self.api_client.create_workspace(self.request.to_api_model())


class CreateWorkspaceJupyterCommand(CreateWorkspaceCommand):
    def _execute_api_call(self) -> WorkspaceCreateResponse:
        return self.api_client.create_workspace(self.request.to_api_model())


class CreateWorkspaceLLMInferenceCommand(
    ExalsiusAPICommand[
        WorkspacesApi, CreateWorkspaceRequestDTO, WorkspaceCreateResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceCreateResponse:
        return self.api_client.create_workspace(self.request.to_api_model())


class CreateWorkspaceDilocoCommand(
    ExalsiusAPICommand[
        WorkspacesApi, CreateWorkspaceRequestDTO, WorkspaceCreateResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceCreateResponse:
        return self.api_client.create_workspace(self.request.to_api_model())


class DeleteWorkspaceCommand(
    ExalsiusAPICommand[
        WorkspacesApi, DeleteWorkspaceRequestDTO, WorkspaceDeleteResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceDeleteResponse:
        return self.api_client.delete_workspace(workspace_id=self.request.workspace_id)

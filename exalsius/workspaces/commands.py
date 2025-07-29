from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.workspaces.models import (
    CreateJupyterWorkspaceRequestDTO,
    CreateLLMInferenceWorkspaceRequestDTO,
    CreatePodWorkspaceRequestDTO,
    CreateWorkspaceRequestDTO,
    DeleteWorkspaceRequestDTO,
    GetWorkspaceRequestDTO,
    WorkspacesListRequestDTO,
)


class ListWorkspacesCommand(BaseCommand[WorkspacesListResponse]):
    def __init__(self, request: WorkspacesListRequestDTO):
        self.request: WorkspacesListRequestDTO = request

    def execute(self) -> WorkspacesListResponse:
        return self.request.api.list_workspaces(cluster_id=self.request.cluster_id)


class GetWorkspaceCommand(BaseCommand[WorkspaceResponse]):
    def __init__(self, request: GetWorkspaceRequestDTO):
        self.request: GetWorkspaceRequestDTO = request

    def execute(self) -> WorkspaceResponse:
        return self.request.api.describe_workspace(
            workspace_id=self.request.workspace_id
        )


class CreateWorkspaceCommand(BaseCommand[WorkspaceCreateResponse]):
    def __init__(
        self,
        request: CreateWorkspaceRequestDTO,
    ):
        self.request: CreateWorkspaceRequestDTO = request

    def execute(self) -> WorkspaceCreateResponse:
        return self.request.api.create_workspace(self.request.to_api_model())


class CreateWorkspacePodCommand(CreateWorkspaceCommand):
    def __init__(
        self,
        request: CreatePodWorkspaceRequestDTO,
    ):
        super().__init__(request)


class CreateWorkspaceJupyterCommand(CreateWorkspaceCommand):
    def __init__(
        self,
        request: CreateJupyterWorkspaceRequestDTO,
    ):
        super().__init__(request)


class CreateWorkspaceLLMInferenceCommand(CreateWorkspaceCommand):
    def __init__(
        self,
        request: CreateLLMInferenceWorkspaceRequestDTO,
    ):
        super().__init__(request)


class DeleteWorkspaceCommand(BaseCommand[WorkspaceDeleteResponse]):
    def __init__(self, request: DeleteWorkspaceRequestDTO):
        self.request: DeleteWorkspaceRequestDTO = request

    def execute(self) -> WorkspaceDeleteResponse:
        return self.request.api.delete_workspace(workspace_id=self.request.workspace_id)

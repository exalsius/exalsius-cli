from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.workspaces.commands import (
    CreateWorkspaceJupyterCommand,
    CreateWorkspaceLLMInferenceCommand,
    CreateWorkspacePodCommand,
    DeleteWorkspaceCommand,
    GetWorkspaceCommand,
    ListWorkspacesCommand,
)
from exalsius.workspaces.models import (
    CreateWorkspaceRequestDTO,
    DeleteWorkspaceRequestDTO,
    GetWorkspaceRequestDTO,
    ResourcePoolDTO,
    WorkspacesListRequestDTO,
    WorkspaceTemplates,
)


class WorkspacesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def list_workspaces(self, cluster_id: str) -> WorkspacesListResponse:
        return self.execute_command(
            ListWorkspacesCommand(
                request=WorkspacesListRequestDTO(
                    cluster_id=cluster_id,
                    api=self.workspaces_api,
                )
            )
        )

    def get_workspace(self, workspace_id: str) -> WorkspaceResponse:
        return self.execute_command(
            GetWorkspaceCommand(
                request=GetWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    workspace_id=workspace_id,
                )
            )
        )

    def create_workspace(
        self,
        cluster_id: str,
        name: str,
        workspace_type: WorkspaceTemplates,
        resources: ResourcePoolDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
        jupyter_password: Optional[str] = None,
        huggingface_model: str = "microsoft/phi-4",
        huggingface_token: Optional[str] = None,
    ) -> WorkspaceCreateResponse:
        workspace_template: WorkspaceTemplate = (
            workspace_type.create_workspace_template()
        )
        if workspace_type == WorkspaceTemplates.JUPYTER:
            if jupyter_password:
                workspace_template.variables["notebookPassword"] = jupyter_password

            command = CreateWorkspaceJupyterCommand(
                request=CreateWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=workspace_template,
                )
            )
        elif workspace_type == WorkspaceTemplates.POD:
            command = CreateWorkspacePodCommand(
                request=CreateWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=workspace_template,
                )
            )
        elif workspace_type == WorkspaceTemplates.LLM_INFERENCE:
            if huggingface_model:
                workspace_template.variables["llmModelName"] = huggingface_model
            if huggingface_token:
                workspace_template.variables["huggingFaceToken"] = huggingface_token

            command = CreateWorkspaceLLMInferenceCommand(
                request=CreateWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=workspace_template,
                )
            )
        return self.execute_command(command)

    def delete_workspace(self, workspace_id: str) -> WorkspaceDeleteResponse:
        return self.execute_command(
            DeleteWorkspaceCommand(
                request=DeleteWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    workspace_id=workspace_id,
                )
            )
        )

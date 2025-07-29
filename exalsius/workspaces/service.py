from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
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
    CreateJupyterWorkspaceRequestDTO,
    CreateLLMInferenceWorkspaceRequestDTO,
    CreatePodWorkspaceRequestDTO,
    DeleteWorkspaceRequestDTO,
    GetWorkspaceRequestDTO,
    ResourcePoolDTO,
    WorkspaceJupyterTemplateDTO,
    WorkspaceLLMInferenceTemplateDTO,
    WorkspacePodTemplateDTO,
    WorkspacesListRequestDTO,
    WorkspaceType,
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
        workspace_type: WorkspaceType,
        resources: ResourcePoolDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
        jupyter_password: Optional[str] = None,
        huggingface_model: str = "microsoft/phi-4",
        huggingface_token: Optional[str] = None,
    ) -> WorkspaceCreateResponse:
        if workspace_type == WorkspaceType.JUPYTER:
            command = CreateWorkspaceJupyterCommand(
                request=CreateJupyterWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=WorkspaceJupyterTemplateDTO(
                        name=workspace_type.value,
                        jupyter_password=jupyter_password,
                    ),
                )
            )
        elif workspace_type == WorkspaceType.POD:
            command = CreateWorkspacePodCommand(
                request=CreatePodWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=WorkspacePodTemplateDTO(
                        name=workspace_type.value,
                    ),
                )
            )
        elif workspace_type == WorkspaceType.LLM_INFERENCE:
            command = CreateWorkspaceLLMInferenceCommand(
                request=CreateLLMInferenceWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    cluster_id=cluster_id,
                    name=name,
                    resources=resources,
                    description=description,
                    to_be_deleted_at=to_be_deleted_at,
                    template=WorkspaceLLMInferenceTemplateDTO(
                        name=workspace_type.value,
                        huggingface_model=huggingface_model,
                        huggingface_token=huggingface_token,
                    ),
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

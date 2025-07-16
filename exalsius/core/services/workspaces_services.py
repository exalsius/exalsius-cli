from typing import Optional, Tuple

from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.models.workspaces import WorkspaceType
from exalsius.core.operations.workspaces_operations import (
    CreateWorkspaceJupyterOperation,
    CreateWorkspaceLLMInferenceOperation,
    CreateWorkspacePodOperation,
    DeleteWorkspaceOperation,
    GetWorkspaceOperation,
    ListWorkspacesOperation,
)
from exalsius.core.services.base import BaseServiceWithAuth


class WorkspacesService(BaseServiceWithAuth):
    def list_workspaces(
        self, cluster_id: str
    ) -> Tuple[Optional[WorkspacesListResponse], Optional[str]]:
        return self.execute_operation(
            ListWorkspacesOperation(
                self.api_client,
                cluster_id,
            )
        )

    def get_workspace(
        self, workspace_id: str
    ) -> Tuple[Optional[WorkspaceResponse], Optional[str]]:
        return self.execute_operation(
            GetWorkspaceOperation(self.api_client, workspace_id)
        )

    def create_workspace(
        self,
        cluster_id: str,
        name: str,
        gpu_count: int,
        owner: str,
        workspace_type: WorkspaceType,
        jupyter_password: Optional[str] = None,
        huggingface_model: Optional[str] = None,
        huggingface_token: Optional[str] = None,
    ) -> Tuple[Optional[WorkspaceCreateResponse], Optional[str]]:
        if workspace_type == WorkspaceType.JUPYTER:
            operation = CreateWorkspaceJupyterOperation(
                self.api_client, cluster_id, name, owner, gpu_count, jupyter_password
            )
        elif workspace_type == WorkspaceType.POD:
            operation = CreateWorkspacePodOperation(
                self.api_client, cluster_id, name, owner, gpu_count
            )
        elif workspace_type == WorkspaceType.LLM_INFERENCE:
            operation = CreateWorkspaceLLMInferenceOperation(
                self.api_client,
                cluster_id,
                name,
                owner,
                gpu_count,
                huggingface_model,
                huggingface_token,
            )
        return self.execute_operation(operation)

    def delete_workspace(
        self, workspace_id: str
    ) -> Tuple[Optional[WorkspaceDeleteResponse], Optional[str]]:
        return self.execute_operation(
            DeleteWorkspaceOperation(self.api_client, workspace_id)
        )

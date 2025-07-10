from typing import Optional, Tuple

from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.models.workspaces import WorkspaceType
from exalsius.core.operations.workspaces_operations import (
    CreateWorkspaceJupyterOperation,
    CreateWorkspacePodOperation,
    DeleteWorkspaceOperation,
    GetWorkspaceOperation,
    ListWorkspacesOperation,
)
from exalsius.core.services.base import BaseService


class WorkspacesService(BaseService):
    def list_workspaces(
        self, cluster_id: str
    ) -> Tuple[WorkspacesListResponse, Optional[str]]:
        return self.execute_operation(
            ListWorkspacesOperation(
                self.api_client,
                cluster_id,
            )
        )

    def get_workspace(
        self, workspace_id: str
    ) -> Tuple[WorkspaceResponse, Optional[str]]:
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
    ) -> Tuple[WorkspaceCreateResponse, Optional[str]]:
        if workspace_type == WorkspaceType.JUPYTER:
            operation = CreateWorkspaceJupyterOperation(
                self.api_client, cluster_id, name, owner, gpu_count
            )
        elif workspace_type == WorkspaceType.POD:
            operation = CreateWorkspacePodOperation(
                self.api_client, cluster_id, name, owner, gpu_count
            )
        return self.execute_operation(operation)

    def delete_workspace(
        self, workspace_id: str
    ) -> Tuple[WorkspaceDeleteResponse, Optional[str]]:
        return self.execute_operation(
            DeleteWorkspaceOperation(self.api_client, workspace_id)
        )

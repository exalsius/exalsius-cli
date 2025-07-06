from typing import Optional, Tuple

from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.operations.workspaces_operations import (
    CreateWorkspaceOperation,
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
    ) -> Tuple[WorkspaceResponse, Optional[str]]:
        return self.execute_operation(
            CreateWorkspaceOperation(
                self.api_client,
                cluster_id,
                name,
                owner,
                gpu_count,
            )
        )

    def delete_workspace(
        self, workspace_id: str
    ) -> Tuple[WorkspaceResponse, Optional[str]]:
        return self.execute_operation(
            DeleteWorkspaceOperation(self.api_client, workspace_id)
        )

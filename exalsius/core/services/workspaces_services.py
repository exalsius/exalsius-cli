from typing import Optional, Tuple

from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.operations.workspaces_operations import ListWorkspacesOperation
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

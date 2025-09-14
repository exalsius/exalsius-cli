from datetime import datetime
from typing import Optional

from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse

from exalsius.config import AppConfig
from exalsius.workspaces.diloco.models import (
    DilocoWorkspaceTemplateDTO,
    DilocoWorkspaceVariablesDTO,
)
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)
from exalsius.workspaces.service import WorkspacesService


class DilocoWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def create_diloco_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: DilocoWorkspaceVariablesDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> WorkspaceCreateResponse:
        return self._create_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            workspace_template=DilocoWorkspaceTemplateDTO(variables=variables),
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )

from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi

from exalsius.config import AppConfig
from exalsius.workspaces.marimo.models import (
    MarimoWorkspaceTemplateDTO,
    MarimoWorkspaceVariablesDTO,
)
from exalsius.workspaces.models import ResourcePoolDTO
from exalsius.workspaces.service import WorkspacesService


class MarimoWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def create_marimo_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: MarimoWorkspaceVariablesDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> str:
        return self._create_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            workspace_template=MarimoWorkspaceTemplateDTO(variables=variables),
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )

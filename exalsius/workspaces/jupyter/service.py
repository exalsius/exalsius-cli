from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi

from exalsius.config import AppConfig
from exalsius.workspaces.jupyter.models import (
    JupyterWorkspaceTemplateDTO,
    JupyterWorkspaceVariablesDTO,
)
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)
from exalsius.workspaces.service import WorkspacesService


class JupyterWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def create_jupyter_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: JupyterWorkspaceVariablesDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> str:
        return self._create_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            workspace_template=JupyterWorkspaceTemplateDTO(variables=variables),
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )

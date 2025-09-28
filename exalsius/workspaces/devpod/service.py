from datetime import datetime
from typing import Optional

from exalsius.config import AppConfig
from exalsius.workspaces.devpod.models import (
    DevPodWorkspaceTemplateDTO,
    DevPodWorkspaceVariablesDTO,
)
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)
from exalsius.workspaces.service import WorkspacesService


class DevPodWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def create_devpod_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: DevPodWorkspaceVariablesDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> str:
        return self._create_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            workspace_template=DevPodWorkspaceTemplateDTO(
                variables=variables,
            ),
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )

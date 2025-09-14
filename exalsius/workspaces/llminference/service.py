from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse

from exalsius.config import AppConfig
from exalsius.workspaces.llminference.models import (
    LLMInferenceWorkspaceTemplateDTO,
    LLMInferenceWorkspaceVariablesDTO,
)
from exalsius.workspaces.models import (
    ResourcePoolDTO,
)
from exalsius.workspaces.service import WorkspacesService


class LLMInferenceWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def create_llm_inference_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: LLMInferenceWorkspaceVariablesDTO,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> WorkspaceCreateResponse:
        return self._create_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            workspace_template=LLMInferenceWorkspaceTemplateDTO(variables=variables),
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )

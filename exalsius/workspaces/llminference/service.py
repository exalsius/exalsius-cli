from datetime import datetime
from typing import Optional

from exalsius.config import AppConfig
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.workspaces.domain import (
    CreateWorkspaceParams,
    Resources,
    WorkspaceTemplate,
)
from exalsius.workspaces.dtos import ResourcePoolDTO
from exalsius.workspaces.service import WorkspacesService


class LLMInferenceWorkspacesService(WorkspacesService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    @handle_service_errors("creating llm-inference workspace")
    def create_llm_inference_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        variables: dict,
        description: Optional[str] = None,
        to_be_deleted_at: Optional[datetime] = None,
    ) -> str:
        resources_domain = Resources(sdk_model=resources.to_api_model())

        template_domain = WorkspaceTemplate(
            name="ray-llm-service-template",
            variables=variables,
        )

        create_params = CreateWorkspaceParams(
            cluster_id=cluster_id,
            name=name,
            resources=resources_domain,
            template=template_domain,
            description=description,
            to_be_deleted_at=to_be_deleted_at,
        )
        return self.workspaces_gateway.create(create_params)

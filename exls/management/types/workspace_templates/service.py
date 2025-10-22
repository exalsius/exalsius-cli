from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.management.types.workspace_templates.domain import (
    WorkspaceTemplate,
    WorkspaceTemplateFilterParams,
)
from exls.management.types.workspace_templates.dtos import (
    ListWorkspaceTemplatesRequestDTO,
    WorkspaceTemplateDTO,
)
from exls.management.types.workspace_templates.gateway.base import (
    WorkspaceTemplatesGateway,
)


class WorkspaceTemplatesService:
    def __init__(self, workspace_templates_gateway: WorkspaceTemplatesGateway):
        self.workspace_templates_gateway = workspace_templates_gateway

    @handle_service_errors("listing workspace templates")
    def list_workspace_templates(
        self, request: ListWorkspaceTemplatesRequestDTO
    ) -> List[WorkspaceTemplateDTO]:
        workspace_templates: List[WorkspaceTemplate] = (
            self.workspace_templates_gateway.list(WorkspaceTemplateFilterParams())
        )
        return [
            WorkspaceTemplateDTO.from_domain(template)
            for template in workspace_templates
        ]


def get_workspace_templates_service(
    config: AppConfig, access_token: str
) -> WorkspaceTemplatesService:
    gateway_factory = GatewayFactory(config=config, access_token=access_token)
    workspace_templates_gateway: WorkspaceTemplatesGateway = (
        gateway_factory.create_workspace_templates_gateway()
    )
    return WorkspaceTemplatesService(
        workspace_templates_gateway=workspace_templates_gateway
    )

from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exls.management.types.workspace_templates.domain import (
    WorkspaceTemplate,
)
from exls.management.types.workspace_templates.gateway.base import (
    WorkspaceTemplatesGateway,
)
from exls.management.types.workspace_templates.gateway.commands import (
    ListWorkspaceTemplatesSdkCommand,
)


class WorkspaceTemplatesGatewaySdk(WorkspaceTemplatesGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list(self) -> List[WorkspaceTemplate]:
        command = ListWorkspaceTemplatesSdkCommand(self._management_api, params=None)
        response: WorkspaceTemplateListResponse = command.execute()
        return [
            WorkspaceTemplate(sdk_model=template)
            for template in response.workspace_templates
        ]

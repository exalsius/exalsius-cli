from typing import List

from exalsius_api_client.api.management_api import ManagementApi

from exls.management.types.workspace_templates.domain import (
    WorkspaceTemplate,
    WorkspaceTemplateFilterParams,
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

    def list(self, params: WorkspaceTemplateFilterParams) -> List[WorkspaceTemplate]:
        command = ListWorkspaceTemplatesSdkCommand(self._management_api, params)
        response: List[WorkspaceTemplate] = command.execute()
        return response

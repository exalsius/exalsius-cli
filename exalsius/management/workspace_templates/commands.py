from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.management.workspace_templates.models import (
    ListWorkspaceTemplatesRequestDTO,
)


class ListWorkspaceTemplatesCommand(
    ExalsiusAPICommand[
        ManagementApi, ListWorkspaceTemplatesRequestDTO, WorkspaceTemplateListResponse
    ]
):
    def _execute_api_call(self) -> WorkspaceTemplateListResponse:
        return self.api_client.list_workspace_templates()

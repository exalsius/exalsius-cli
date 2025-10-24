from typing import Optional

from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand


class ListWorkspaceTemplatesSdkCommand(
    BaseManagementSdkCommand[None, WorkspaceTemplateListResponse]
):
    def _execute_api_call(
        self, params: Optional[None]
    ) -> WorkspaceTemplateListResponse:
        response: WorkspaceTemplateListResponse = (
            self.api_client.list_workspace_templates()
        )
        return response

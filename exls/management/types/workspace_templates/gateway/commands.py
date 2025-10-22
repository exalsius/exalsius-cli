from typing import List, Optional

from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand
from exls.management.types.workspace_templates.domain import (
    WorkspaceTemplate,
    WorkspaceTemplateFilterParams,
)


class ListWorkspaceTemplatesSdkCommand(
    BaseManagementSdkCommand[WorkspaceTemplateFilterParams, List[WorkspaceTemplate]]
):
    def _execute_api_call(
        self, params: Optional[WorkspaceTemplateFilterParams]
    ) -> List[WorkspaceTemplate]:
        response: WorkspaceTemplateListResponse = (
            self.api_client.list_workspace_templates()
        )
        return [
            WorkspaceTemplate(sdk_model=template)
            for template in response.workspace_templates
        ]

from typing import List

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exalsius.core.base.commands import BaseCommand
from exalsius.management.workspace_templates.models import (
    ListWorkspaceTemplatesRequestDTO,
)


class ListWorkspaceTemplatesCommand(BaseCommand):
    def __init__(self, request: ListWorkspaceTemplatesRequestDTO):
        self.request: ListWorkspaceTemplatesRequestDTO = request

    def execute(self) -> List[WorkspaceTemplate]:
        response: WorkspaceTemplateListResponse = (
            self.request.api.list_workspace_templates()
        )
        return response.workspace_templates

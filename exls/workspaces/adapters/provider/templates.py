from typing import List

from exls.management.core.domain import WorkspaceTemplate as ManagementWorkspaceTemplate
from exls.management.core.service import ManagementService
from exls.workspaces.core.domain import WorkspaceTemplate
from exls.workspaces.core.ports.providers import WorkspaceTemplatesProvider


class WorkspaceTemplatesDomainProvider(WorkspaceTemplatesProvider):
    def __init__(self, management_service: ManagementService):
        self._management_service: ManagementService = management_service

    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        templates: List[ManagementWorkspaceTemplate] = (
            self._management_service.list_workspace_templates()
        )
        return [
            WorkspaceTemplate(
                id_name=template.name,
                variables=template.variables,
            )
            for template in templates
        ]

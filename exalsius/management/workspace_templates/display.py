from typing import Dict, List

from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exalsius.core.commons.render.json import JsonListStringRenderer
from exalsius.core.commons.render.table import Column, TableListRenderer, get_column
from exalsius.management.workspace_templates.models import (
    RenderableWorkspaceTemplateDTO,
)


class JsonWorkspaceTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: JsonListStringRenderer[
            WorkspaceTemplate
        ] = JsonListStringRenderer[WorkspaceTemplate](),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(self, workspace_templates: List[WorkspaceTemplate]):
        self.workspace_templates_list_display.display(workspace_templates)


DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "variables": get_column("Variables"),
    "description": get_column("Description"),
}


class TableWorkspaceTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: TableListRenderer[
            RenderableWorkspaceTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(self, workspace_templates: List[WorkspaceTemplate]):
        renderable_workspace_templates: List[RenderableWorkspaceTemplateDTO] = [
            RenderableWorkspaceTemplateDTO(
                name=workspace_template.name,
                description=workspace_template.description or "",
                variables=", ".join(workspace_template.variables.keys()),
            )
            for workspace_template in workspace_templates
        ]
        self.workspace_templates_list_display.display(renderable_workspace_templates)

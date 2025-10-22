from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exls.core.commons.render.json import JsonListStringRenderer
from exls.core.commons.render.table import Column, TableListRenderer, get_column
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO


class JsonWorkspaceTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: JsonListStringRenderer[
            WorkspaceTemplateDTO
        ] = JsonListStringRenderer[WorkspaceTemplateDTO](),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(
        self, workspace_templates: List[WorkspaceTemplateDTO]
    ):
        self.workspace_templates_list_display.display(workspace_templates)


DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "description": get_column("Description"),
}


class TableWorkspaceTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: TableListRenderer[
            WorkspaceTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(
        self, workspace_templates: List[WorkspaceTemplateDTO]
    ):
        self.workspace_templates_list_display.display(workspace_templates)

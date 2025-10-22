from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exls.core.commons.render.json import JsonListStringRenderer
from exls.core.commons.render.table import Column, TableListRenderer, get_column
from exls.management.types.service_templates.dtos import ServiceTemplateDTO


class JsonServiceTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        service_templates_list_renderer: JsonListStringRenderer[
            ServiceTemplateDTO
        ] = JsonListStringRenderer[ServiceTemplateDTO](),
    ):
        super().__init__()
        self.service_templates_list_display = ConsoleListDisplay(
            renderer=service_templates_list_renderer
        )

    def display_service_templates(self, service_templates: List[ServiceTemplateDTO]):
        self.service_templates_list_display.display(service_templates)


DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "description": get_column("Description"),
}


class TableServiceTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        service_templates_list_renderer: TableListRenderer[
            ServiceTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.service_templates_list_display = ConsoleListDisplay(
            renderer=service_templates_list_renderer
        )

    def display_service_templates(self, service_templates: List[ServiceTemplateDTO]):
        self.service_templates_list_display.display(service_templates)

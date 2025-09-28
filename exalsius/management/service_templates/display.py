from typing import Dict, List

from exalsius_api_client.models.service_template import ServiceTemplate

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exalsius.core.commons.render.json import JsonListStringRenderer
from exalsius.core.commons.render.table import Column, TableListRenderer, get_column
from exalsius.management.service_templates.models import RenderableServiceTemplateDTO


class JsonServiceTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        service_templates_list_renderer: JsonListStringRenderer[
            ServiceTemplate
        ] = JsonListStringRenderer[ServiceTemplate](),
    ):
        super().__init__()
        self.service_templates_list_display = ConsoleListDisplay(
            renderer=service_templates_list_renderer
        )

    def display_service_templates(self, service_templates: List[ServiceTemplate]):
        self.service_templates_list_display.display(service_templates)


DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "variables": get_column("Variables Names"),
    "description": get_column("Description"),
}


class TableServiceTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        service_templates_list_renderer: TableListRenderer[
            RenderableServiceTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.service_templates_list_display = ConsoleListDisplay(
            renderer=service_templates_list_renderer
        )

    def display_service_templates(self, service_templates: List[ServiceTemplate]):
        renderable_service_templates: List[RenderableServiceTemplateDTO] = [
            RenderableServiceTemplateDTO(
                name=service_template.name,
                description=service_template.description or "",
                variables=", ".join(service_template.variables.keys()),
            )
            for service_template in service_templates
        ]
        self.service_templates_list_display.display(renderable_service_templates)

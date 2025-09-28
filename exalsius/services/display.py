from typing import Dict, List

from exalsius_api_client.models.service import Service

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exalsius.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exalsius.core.commons.render.table import (
    Column,
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)


class JsonServicesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        services_list_renderer: JsonListStringRenderer[
            Service
        ] = JsonListStringRenderer[Service](),
        services_single_item_renderer: JsonSingleItemStringRenderer[
            Service
        ] = JsonSingleItemStringRenderer[Service](),
    ):
        super().__init__()
        self.services_list_display = ConsoleListDisplay(renderer=services_list_renderer)
        self.services_single_item_display = ConsoleSingleItemDisplay(
            renderer=services_single_item_renderer
        )

    def display_services(self, services: List[Service]):
        self.services_list_display.display(services)

    def display_service(self, service: Service):
        self.services_single_item_display.display(service)


DEFAULT_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "service_template": get_column("Service Template"),
    "created_at": get_column("Created At"),
}


class TableServicesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        services_list_renderer: TableListRenderer[Service] = TableListRenderer[Service](
            columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP
        ),
        services_single_item_renderer: TableSingleItemRenderer[
            Service
        ] = TableSingleItemRenderer[Service](columns_map=DEFAULT_COLUMNS_RENDERING_MAP),
    ):
        super().__init__()
        self.services_list_display = ConsoleListDisplay(renderer=services_list_renderer)
        self.services_single_item_display = ConsoleSingleItemDisplay(
            renderer=services_single_item_renderer
        )

    def display_services(self, services: List[Service]):
        self.services_list_display.display(services)

    def display_service(self, service: Service):
        self.services_single_item_display.display(service)

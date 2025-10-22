from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exls.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exls.core.commons.render.table import (
    Column,
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)
from exls.services.dtos import ServiceDTO


class JsonServicesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        services_list_renderer: JsonListStringRenderer[
            ServiceDTO
        ] = JsonListStringRenderer[ServiceDTO](),
        services_single_item_renderer: JsonSingleItemStringRenderer[
            ServiceDTO
        ] = JsonSingleItemStringRenderer[ServiceDTO](),
    ):
        super().__init__()
        self.services_list_display = ConsoleListDisplay(renderer=services_list_renderer)
        self.services_single_item_display = ConsoleSingleItemDisplay(
            renderer=services_single_item_renderer
        )

    def display_services(self, services: List[ServiceDTO]):
        self.services_list_display.display(services)

    def display_service(self, service: ServiceDTO):
        self.services_single_item_display.display(service)


DEFAULT_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "cluster_id": get_column("Cluster ID"),
    "service_template": get_column("Service Template"),
    "created_at": get_column("Created At"),
}


class TableServicesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        services_list_renderer: TableListRenderer[ServiceDTO] = TableListRenderer[
            ServiceDTO
        ](columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP),
        services_single_item_renderer: TableSingleItemRenderer[
            ServiceDTO
        ] = TableSingleItemRenderer[ServiceDTO](
            columns_map=DEFAULT_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.services_list_display = ConsoleListDisplay(renderer=services_list_renderer)
        self.services_single_item_display = ConsoleSingleItemDisplay(
            renderer=services_single_item_renderer
        )

    def display_services(self, services: List[ServiceDTO]):
        self.services_list_display.display(services)

    def display_service(self, service: ServiceDTO):
        self.services_single_item_display.display(service)

from typing import List

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
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)
from exalsius.nodes.dtos import CloudNodeDTO, NodeDTO, SelfManagedNodeDTO


class JsonNodesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: JsonListStringRenderer[
            CloudNodeDTO
        ] = JsonListStringRenderer[CloudNodeDTO](),
        self_managed_nodes_list_renderer: JsonListStringRenderer[
            SelfManagedNodeDTO
        ] = JsonListStringRenderer[SelfManagedNodeDTO](),
        cloud_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            CloudNodeDTO
        ] = JsonSingleItemStringRenderer[CloudNodeDTO](),
        self_managed_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            SelfManagedNodeDTO
        ] = JsonSingleItemStringRenderer[SelfManagedNodeDTO](),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay(
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay(
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=self_managed_nodes_single_item_renderer
        )

    def display_nodes(self, data: List[NodeDTO]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNodeDTO)]
        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNodeDTO)
        ]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: NodeDTO):
        if isinstance(data, CloudNodeDTO):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNodeDTO):
            self.self_managed_nodes_single_item_display.display(data)


DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "hostname": get_column("Hostname"),
    "import_time": get_column("Import Time"),
    "node_status": get_column("Status"),
    "provider": get_column("Provider"),
    "instance_type": get_column("Instance Type"),
    "price_per_hour": get_column("Price"),
}

DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "hostname": get_column("Hostname"),
    "import_time": get_column("Import Time"),
    "node_status": get_column("Status"),
    "endpoint": get_column("Endpoint"),
}


class TableNodesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: TableListRenderer[CloudNodeDTO] = TableListRenderer[
            CloudNodeDTO
        ](columns_rendering_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP),
        self_managed_nodes_list_renderer: TableListRenderer[
            SelfManagedNodeDTO
        ] = TableListRenderer[SelfManagedNodeDTO](
            columns_rendering_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
        cloud_nodes_single_item_renderer: TableSingleItemRenderer[
            CloudNodeDTO
        ] = TableSingleItemRenderer[CloudNodeDTO](
            columns_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP
        ),
        self_managed_nodes_single_item_renderer: TableSingleItemRenderer[
            SelfManagedNodeDTO
        ] = TableSingleItemRenderer[SelfManagedNodeDTO](
            columns_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay(
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay(
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=self_managed_nodes_single_item_renderer
        )

    def display_nodes(self, data: List[NodeDTO]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNodeDTO)]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)

        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNodeDTO)
        ]
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: NodeDTO):
        if isinstance(data, CloudNodeDTO):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNodeDTO):
            self.self_managed_nodes_single_item_display.display(data)

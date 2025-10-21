from typing import List

from exalsius.clusters.dtos import (
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
)
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

# TODO: We probably need a available / occupied resources DTO


class JsonClusterDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        cluster_list_renderer: JsonListStringRenderer[
            ClusterDTO
        ] = JsonListStringRenderer[ClusterDTO](),
        cluster_single_item_renderer: JsonSingleItemStringRenderer[
            ClusterDTO
        ] = JsonSingleItemStringRenderer[ClusterDTO](),
        cluster_nodes_list_renderer: JsonListStringRenderer[
            ClusterNodeDTO
        ] = JsonListStringRenderer[ClusterNodeDTO](),
        cluster_resources_list_renderer: JsonListStringRenderer[
            ClusterNodeResourcesDTO
        ] = JsonListStringRenderer[ClusterNodeResourcesDTO](),
    ):
        super().__init__()
        self.cluster_list_display = ConsoleListDisplay(renderer=cluster_list_renderer)
        self.cluster_single_item_display = ConsoleSingleItemDisplay(
            renderer=cluster_single_item_renderer
        )
        self.cluster_nodes_list_display = ConsoleListDisplay(
            renderer=cluster_nodes_list_renderer
        )
        self.cluster_resources_list_display = ConsoleListDisplay(
            renderer=cluster_resources_list_renderer
        )

    def display_clusters(self, data: List[ClusterDTO]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: ClusterDTO):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterNodeResourcesDTO]):
        self.cluster_resources_list_display.display(data)


DEFAULT_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "cluster_status": get_column("Status"),
    "created_at": get_column("Created At"),
    "updated_at": get_column("Updated At"),
}

DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP = {
    "node_hostname": get_column("Hostname"),
    "node_role": get_column("Role"),
    "node_status": get_column("Status"),
    "node_ip_address": get_column("IP Address"),
}

DEFAULT_CLUSTER_RESOURCES_COLUMNS_RENDERING_MAP = {
    "cluster_name": get_column("Cluster Name"),
    "node_hostname": get_column("Node Hostname"),
    "free_resources.gpu_type": get_column("GPU Type"),
    "free_resources.gpu_count": get_column("GPU Count"),
    "free_resources.cpu": get_column("CPU Cores"),
    "free_resources.memory": get_column("Memory GB"),
    "free_resources.storage": get_column("Storage GB"),
}


class TableClusterDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        cluster_list_renderer: TableListRenderer[ClusterDTO] = TableListRenderer[
            ClusterDTO
        ](columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP),
        cluster_single_item_renderer: TableSingleItemRenderer[
            ClusterDTO
        ] = TableSingleItemRenderer[ClusterDTO](
            columns_map=DEFAULT_COLUMNS_RENDERING_MAP
        ),
        cluster_nodes_list_renderer: TableListRenderer[
            ClusterNodeDTO
        ] = TableListRenderer[ClusterNodeDTO](
            columns_rendering_map=DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP
        ),
        cluster_resources_list_renderer: TableListRenderer[
            ClusterNodeResourcesDTO
        ] = TableListRenderer[ClusterNodeResourcesDTO](
            columns_rendering_map=DEFAULT_CLUSTER_RESOURCES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cluster_list_display = ConsoleListDisplay(renderer=cluster_list_renderer)
        self.cluster_single_item_display = ConsoleSingleItemDisplay(
            renderer=cluster_single_item_renderer
        )
        self.cluster_nodes_list_display = ConsoleListDisplay(
            renderer=cluster_nodes_list_renderer
        )
        self.cluster_resources_list_display = ConsoleListDisplay(
            renderer=cluster_resources_list_renderer
        )

    def display_clusters(self, data: List[ClusterDTO]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: ClusterDTO):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterNodeResourcesDTO]):
        self.cluster_resources_list_display.display(data)

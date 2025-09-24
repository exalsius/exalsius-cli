from typing import List

from exalsius_api_client.models.cluster import Cluster

from exalsius.clusters.models import ClusterNodeDTO, ClusterResourcesDTO
from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
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
        cluster_list_renderer: BaseListRenderer[Cluster, str] = JsonListStringRenderer[
            Cluster
        ](),
        cluster_single_item_renderer: BaseSingleItemRenderer[
            Cluster, str
        ] = JsonSingleItemStringRenderer[Cluster](),
        cluster_nodes_list_renderer: BaseListRenderer[
            ClusterNodeDTO, str
        ] = JsonListStringRenderer[ClusterNodeDTO](),
        cluster_resources_list_renderer: BaseListRenderer[
            ClusterResourcesDTO, str
        ] = JsonListStringRenderer[ClusterResourcesDTO](),
    ):
        super().__init__()
        self.cluster_list_display = ConsoleListDisplay[Cluster](
            renderer=cluster_list_renderer
        )
        self.cluster_single_item_display = ConsoleSingleItemDisplay[Cluster](
            renderer=cluster_single_item_renderer
        )
        self.cluster_nodes_list_display = ConsoleListDisplay[ClusterNodeDTO](
            renderer=cluster_nodes_list_renderer
        )
        self.cluster_resources_list_display = ConsoleListDisplay[ClusterResourcesDTO](
            renderer=cluster_resources_list_renderer
        )

    def display_clusters(self, data: List[Cluster]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: Cluster):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterResourcesDTO]):
        self.cluster_resources_list_display.display(data)


DEFAULT_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "cluster_status": get_column("Status"),
    "created_at": get_column("Created At"),
    "updated_at": get_column("Updated At"),
}

DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "role": get_column("Role"),
    "hostname": get_column("Hostname"),
}

DEFAULT_CLUSTER_RESOURCES_COLUMNS_RENDERING_MAP = {
    "node_id": get_column("Node ID", no_wrap=True),
    "gpu_type": get_column("GPU Type"),
    "gpu_count": get_column("GPU Count"),
    "cpu_cores": get_column("CPU Cores"),
    "memory_gb": get_column("Memory GB"),
    "storage_gb": get_column("Storage GB"),
}


class TableClusterDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        cluster_list_renderer: BaseListRenderer[Cluster, str] = TableListRenderer[
            Cluster
        ](columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP),
        cluster_single_item_renderer: BaseSingleItemRenderer[
            Cluster, str
        ] = TableSingleItemRenderer[Cluster](columns_map=DEFAULT_COLUMNS_RENDERING_MAP),
        cluster_nodes_list_renderer: BaseListRenderer[
            ClusterNodeDTO, str
        ] = TableListRenderer[ClusterNodeDTO](
            columns_rendering_map=DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP
        ),
        cluster_resources_list_renderer: BaseListRenderer[
            ClusterResourcesDTO, str
        ] = TableListRenderer[ClusterResourcesDTO](
            columns_rendering_map=DEFAULT_CLUSTER_RESOURCES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cluster_list_display = ConsoleListDisplay[Cluster](
            renderer=cluster_list_renderer
        )
        self.cluster_single_item_display = ConsoleSingleItemDisplay[Cluster](
            renderer=cluster_single_item_renderer
        )
        self.cluster_nodes_list_display = ConsoleListDisplay[ClusterNodeDTO](
            renderer=cluster_nodes_list_renderer
        )
        self.cluster_resources_list_display = ConsoleListDisplay[ClusterResourcesDTO](
            renderer=cluster_resources_list_renderer
        )

    def display_clusters(self, data: List[Cluster]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: Cluster):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterResourcesDTO]):
        self.cluster_resources_list_display.display(data)

from abc import ABC, abstractmethod
from typing import List

from exls.clusters.dtos import (
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    DeployClusterRequestDTO,
)
from exls.core.commons.display import (
    BaseDisplayManager,
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ComposingDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exls.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exls.core.commons.render.table import (
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)


class BaseClusterDisplayManager(BaseDisplayManager, ABC):
    @abstractmethod
    def display_clusters(self, data: List[ClusterDTO]):
        pass

    @abstractmethod
    def display_cluster(self, data: ClusterDTO):
        pass

    @abstractmethod
    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        pass

    @abstractmethod
    def display_cluster_resources(self, data: List[ClusterNodeResourcesDTO]):
        pass

    @abstractmethod
    def display_deploy_cluster_request(self, data: DeployClusterRequestDTO):
        pass


class JsonClusterDisplayManager(BaseJsonDisplayManager, BaseClusterDisplayManager):
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
        deploy_cluster_request_renderer: JsonSingleItemStringRenderer[
            DeployClusterRequestDTO
        ] = JsonSingleItemStringRenderer[DeployClusterRequestDTO](),
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
        self.deploy_cluster_request_display = ConsoleSingleItemDisplay(
            renderer=deploy_cluster_request_renderer
        )

    def display_clusters(self, data: List[ClusterDTO]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: ClusterDTO):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterNodeResourcesDTO]):
        self.cluster_resources_list_display.display(data)

    def display_deploy_cluster_request(self, data: DeployClusterRequestDTO):
        self.deploy_cluster_request_display.display(data)


DEFAULT_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "cluster_status": get_column("Status"),
    "created_at": get_column("Created At"),
    "updated_at": get_column("Updated At"),
}

DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP = {
    "cluster_name": get_column("Cluster Name"),
    "node_hostname": get_column("Hostname"),
    "node_role": get_column("Role"),
    "node_status": get_column("Status"),
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

DEFAULT_DEPLOY_CLUSTER_REQUEST_COLUMNS_RENDERING_MAP = {
    "name": get_column("Name"),
    "cluster_type": get_column("Cluster Type"),
    "gpu_type": get_column("GPU Type"),
    "enable_multinode_training": get_column("Multinode Training"),
    "enable_telemetry": get_column("Telemetry Enabled"),
    "worker_node_ids": get_column("Worker Node IDs"),
}


class TableClusterDisplayManager(BaseTableDisplayManager, BaseClusterDisplayManager):
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
        deploy_cluster_request_renderer: TableSingleItemRenderer[
            DeployClusterRequestDTO
        ] = TableSingleItemRenderer[DeployClusterRequestDTO](
            columns_map=DEFAULT_DEPLOY_CLUSTER_REQUEST_COLUMNS_RENDERING_MAP
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
        self.deploy_cluster_request_display = ConsoleSingleItemDisplay(
            renderer=deploy_cluster_request_renderer
        )

    def display_clusters(self, data: List[ClusterDTO]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: ClusterDTO):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterNodeResourcesDTO]):
        self.cluster_resources_list_display.display(data)

    def display_deploy_cluster_request(self, data: DeployClusterRequestDTO):
        self.deploy_cluster_request_display.display(data)


class ComposingClusterDisplayManager(ComposingDisplayManager):
    def __init__(
        self,
        display_manager: BaseClusterDisplayManager,
    ):
        super().__init__(display_manager=display_manager)
        self.display_manager: BaseClusterDisplayManager = display_manager

    def display_cluster(self, cluster: ClusterDTO):
        self.display_manager.display_cluster(cluster)

    def display_cluster_nodes(self, cluster_nodes: List[ClusterNodeDTO]):
        self.display_manager.display_cluster_nodes(cluster_nodes)

    def display_cluster_resources(
        self, cluster_resources: List[ClusterNodeResourcesDTO]
    ):
        self.display_manager.display_cluster_resources(cluster_resources)

    def display_clusters(self, clusters: List[ClusterDTO]):
        self.display_manager.display_clusters(clusters)

    def display_deploy_cluster_request(
        self, deploy_cluster_request: DeployClusterRequestDTO
    ):
        self.display_manager.display_deploy_cluster_request(deploy_cluster_request)

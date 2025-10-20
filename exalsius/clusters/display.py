# Forward reference for type annotation
from typing import TYPE_CHECKING, List

from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cluster import Cluster

from exalsius.clusters.models import ClusterNodeDTO, ClusterResourcesDTO
from exalsius.core.commons.display import (
    BaseInteractiveDisplay,
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


if TYPE_CHECKING:
    from exalsius.clusters.interactive import ClusterInteractiveConfig


class JsonClusterDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        cluster_list_renderer: JsonListStringRenderer[Cluster] = JsonListStringRenderer[
            Cluster
        ](),
        cluster_single_item_renderer: JsonSingleItemStringRenderer[
            Cluster
        ] = JsonSingleItemStringRenderer[Cluster](),
        cluster_nodes_list_renderer: JsonListStringRenderer[
            ClusterNodeDTO
        ] = JsonListStringRenderer[ClusterNodeDTO](),
        cluster_resources_list_renderer: JsonListStringRenderer[
            ClusterResourcesDTO
        ] = JsonListStringRenderer[ClusterResourcesDTO](),
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
        cluster_list_renderer: TableListRenderer[Cluster] = TableListRenderer[Cluster](
            columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP
        ),
        cluster_single_item_renderer: TableSingleItemRenderer[
            Cluster
        ] = TableSingleItemRenderer[Cluster](columns_map=DEFAULT_COLUMNS_RENDERING_MAP),
        cluster_nodes_list_renderer: TableListRenderer[
            ClusterNodeDTO
        ] = TableListRenderer[ClusterNodeDTO](
            columns_rendering_map=DEFAULT_CLUSTER_NODES_COLUMNS_RENDERING_MAP
        ),
        cluster_resources_list_renderer: TableListRenderer[
            ClusterResourcesDTO
        ] = TableListRenderer[ClusterResourcesDTO](
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

    def display_clusters(self, data: List[Cluster]):
        self.cluster_list_display.display(data)

    def display_cluster(self, data: Cluster):
        self.cluster_single_item_display.display(data)

    def display_cluster_nodes(self, data: List[ClusterNodeDTO]):
        self.cluster_nodes_list_display.display(data)

    def display_cluster_resources(self, data: List[ClusterResourcesDTO]):
        self.cluster_resources_list_display.display(data)


class ClusterInteractiveDisplay(BaseInteractiveDisplay):
    """Display manager for cluster interactive flows."""

    def display_available_nodes(self, nodes: List[BaseNode]):
        """Display available nodes in a compact table format."""
        if not nodes:
            return

        # Use the same table rendering system as other tables
        from exalsius.nodes.display import TableNodesDisplayManager

        nodes_display_manager = TableNodesDisplayManager()

        self.console.print("\n[bold]Available Nodes:[/bold]")
        nodes_display_manager.display_nodes(nodes)

    def display_cluster_creation_summary(self, config: "ClusterInteractiveConfig"):
        """Display cluster configuration summary in a panel."""
        from rich.panel import Panel

        summary_text = f"""
[bold]Name:[/bold] {config.name}
[bold]Type:[/bold] {config.cluster_type.value}
[bold]GPU Type:[/bold] {config.gpu_type.value.title()}
[bold]Diloco Support:[/bold] {'Enabled' if config.diloco_enabled else 'Disabled'}
[bold]Telemetry:[/bold] {'Enabled' if config.telemetry_enabled else 'Disabled'}
[bold]Nodes:[/bold] {len(config.node_ids)} selected
"""

        if config.node_ids:
            worker_count = sum(1 for r in config.node_roles.values() if r == "WORKER")
            cp_count = sum(
                1 for r in config.node_roles.values() if r == "CONTROL_PLANE"
            )
            summary_text += (
                f"  - Workers: {worker_count}\n  - Control Plane: {cp_count}"
            )

        panel = Panel(
            summary_text.strip(), title="Cluster Configuration", border_style="custom"
        )
        self.console.print(panel)

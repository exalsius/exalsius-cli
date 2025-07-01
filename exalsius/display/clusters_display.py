from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.cluster_services_response import ClusterServicesResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from rich.console import Console
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class ClustersDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_clusters(self, cluster_list_response: ClustersListResponse):
        if not cluster_list_response.clusters:
            self.print_info("No clusters found. Please create a cluster.")
            return

        table = Table(
            title="Clusters",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Created At")
        table.add_column("Updated At")
        table.add_column("Control Plane Nodes")
        table.add_column("Worker Nodes")
        table.add_column("Costs per hour")
        table.add_column("Current Costs")
        # TODO add services

        for cluster in cluster_list_response.clusters:
            table.add_row(
                str(cluster.id),
                str(cluster.name),
                str(cluster.cluster_status),
                str(cluster.created_at),
                str(cluster.updated_at),
                str(cluster.control_plane_node_ids),
                str(cluster.worker_node_ids),
                str(cluster.costs_per_hour),
                str(cluster.current_costs),
                # TODO add services
            )

        self.console.print(table)

    def display_cluster(self, cluster_response: ClusterResponse):
        table = Table(
            title="Cluster",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Created At")
        table.add_column("Updated At")
        table.add_column("Control Plane Nodes")
        table.add_column("Worker Nodes")
        table.add_column("Costs per hour")
        table.add_column("Current Costs")
        # TODO add services

        cluster = cluster_response.cluster
        table.add_row(
            str(cluster.id),
            str(cluster.name),
            str(cluster.cluster_status),
            str(cluster.created_at),
            str(cluster.updated_at),
            str(cluster.control_plane_node_ids),
            str(cluster.worker_node_ids),
            str(cluster.costs_per_hour),
            str(cluster.current_costs),
            # TODO add services
        )

        self.console.print(table)

    def display_delete_cluster_message(self, cluster_response: ClusterResponse):
        all_nodes = (
            cluster_response.cluster.control_plane_node_ids
            + cluster_response.cluster.worker_node_ids
        )
        self.print_info(
            f"Cluster {cluster_response.cluster.id} will be deleted. This action is irreversible."
        )
        self.print_info(
            f"The following nodes will be returned to the node pool: {all_nodes}"
        )

    def display_cluster_services(
        self, cluster_services_response: ClusterServicesResponse
    ):
        table = Table(
            title="Cluster Service Deployments",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("Service Name")
        table.add_column("Values")

        for service_deployment in cluster_services_response.services_deployments:
            table.add_row(
                str(service_deployment.service_name),
                str(service_deployment.values),
            )

        self.console.print(table)

    def display_cluster_nodes(self, cluster_nodes_response: ClusterNodesResponse):
        table = Table(
            title="Cluster Nodes",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("Control Plane Nodes")
        table.add_column("Worker Nodes")

        table.add_row(
            str(cluster_nodes_response.control_plane_node_ids),
            str(cluster_nodes_response.worker_node_ids),
        )

        self.console.print(table)

from typing import List

from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.cluster_services_response import ClusterServicesResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from exalsius_api_client.models.credentials import Credentials
from rich.console import Console
from rich.table import Table

from exalsius.core.base.display import BaseDisplayManager


class ClustersDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_clusters(self, cluster_list_response: ClustersListResponse):
        table = Table(
            title="Clusters",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("ID", no_wrap=True)
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Created At")
        table.add_column("Updated At")
        # TODO add services

        for cluster in cluster_list_response.clusters:
            table.add_row(
                str(cluster.id),
                str(cluster.name),
                str(cluster.cluster_status),
                str(cluster.created_at),
                str(cluster.updated_at),
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
        # TODO add services

        cluster = cluster_response.cluster
        table.add_row(
            str(cluster.id),
            str(cluster.name),
            str(cluster.cluster_status),
            str(cluster.created_at),
            str(cluster.updated_at),
        )

        self.console.print(table)

    def display_delete_cluster_message(self, cluster_response: ClusterResponse):
        all_nodes: list[str] = []
        if cluster_response.cluster.control_plane_node_ids:
            all_nodes.extend(cluster_response.cluster.control_plane_node_ids)
        if cluster_response.cluster.worker_node_ids:
            all_nodes.extend(cluster_response.cluster.worker_node_ids)

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

    def display_cluster_resources(
        self, cluster_resources_response: ClusterResourcesListResponse
    ):
        table = Table(
            title="Cluster Resource Availability",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("Node")
        table.add_column("Available GPUs")
        table.add_column("Available CPUs")
        table.add_column("Available Memory")
        table.add_column("Available Storage")

        for node in cluster_resources_response.resources:
            if node and node.available and node.occupied:
                table.add_row(
                    str(node.node_id),
                    str(f"{node.available.gpu_count} GPUs"),
                    str(f"{node.available.cpu_cores} cores"),
                    str(f"{node.available.memory_gb} GB"),
                    str(f"{node.available.storage_gb} GB"),
                )

        self.console.print(table)

    def display_cloud_credentials(self, cloud_credentials: List[Credentials]):
        if not cloud_credentials:
            self.print_info("No cloud credentials found")
            return

        table = Table(
            title="Available Cloud Credentials",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("Name", style="green")
        table.add_column("Description", style="cyan")

        for cloud_credential in cloud_credentials:
            table.add_row(cloud_credential.name, cloud_credential.description)

        self.console.print(table)

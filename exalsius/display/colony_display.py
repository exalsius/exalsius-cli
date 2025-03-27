from rich.console import Console
from rich.table import Table

from exalsius.kubernetes.resources import ResourceManager


class ColonyDisplayManager:
    def __init__(self, console: Console):
        self.console = console
        self.resource_manager = ResourceManager()

    def display_colonies(self, colonies: list[dict]) -> None:
        """
        Display a list of colonies in a table format.

        Args:
            colonies (list[dict]): List of colonies to display
        """
        table = Table(
            title="exalsius Colonies",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Status", style="green", no_wrap=True)
        table.add_column("Creation Time", style="magenta")
        table.add_column("Ready Clusters", style="green")
        table.add_column("Total Clusters", style="green")
        table.add_column("K8s Version", style="blue")
        table.add_column("Nodes", style="blue")

        for colony in colonies:
            metadata = colony.get("metadata", {})
            spec = colony.get("spec", {})
            name = metadata.get("name", "unknown")
            status = colony.get("status", {}).get("phase", "unknown")
            creation_time = metadata.get("creationTimestamp", "unknown")
            ready_clusters = colony.get("status", {}).get("readyClusters", 0)
            total_clusters = colony.get("status", {}).get("totalClusters", 0)
            k8s_version = spec.get("k8sVersion", "unknown")

            nodes = {}
            for cluster in colony.get("status", {}).get("clusterRefs", []):
                cluster_name = cluster.get("name")
                nodes[cluster_name] = self.resource_manager.get_cluster_nodes(
                    cluster_name
                )

            # Convert nodes dict to printable string
            nodes_str = ""
            for cluster_name, cluster_nodes in nodes.items():
                nodes_str += f"{cluster_name}: {len(cluster_nodes)} nodes\n"
            nodes_str = nodes_str.rstrip("\n")

            table.add_row(
                name,
                str(status),
                creation_time,
                str(ready_clusters),
                str(total_clusters),
                k8s_version,
                nodes_str,
            )
        self.console.print(table)

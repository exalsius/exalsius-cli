from typing import List

from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cloud_node import CloudNode
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.self_managed_node import SelfManagedNode
from rich.console import Console
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class NodesDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def _create_node_table(self, title: str) -> Table:
        return Table(
            title=title, show_header=True, header_style="bold", border_style="custom"
        )

    def _add_common_columns(self, table: Table):
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description", style="blue")
        table.add_column("Location", style="green")
        table.add_column("GPU Count", style="blue")
        table.add_column("GPU Vendor", style="green")
        table.add_column("GPU Type", style="blue")
        table.add_column("GPU Memory", style="red")
        table.add_column("CPU Cores", style="green")
        table.add_column("Memory", style="blue")
        table.add_column("Storage", style="red")
        table.add_column("Import Time", style="green")
        table.add_column("Status", style="blue")

    def _add_node_row(self, table: Table, node: BaseNode):
        table.add_row(
            str(node.id),
            str(node.node_type),
            str(node.description),
            str(node.location),
            str(node.gpu_count),
            str(node.gpu_vendor),
            str(node.gpu_type),
            str(node.gpu_memory),
            str(node.cpu_cores),
            str(node.memory_gb),
            str(node.storage_gb),
            str(node.import_time),
            str(node.node_status),
        )

    def _add_cloud_node_specific_columns(self, table: Table):
        """Add columns specific to CloudNode type."""
        table.add_column("Provider", style="cyan")
        table.add_column("Instance Type", style="green")
        table.add_column("Region", style="blue")
        table.add_column("Price", style="red")

    def _add_self_managed_node_specific_columns(self, table: Table):
        """Add columns specific to SelfManagedNode type."""
        table.add_column("IP Address", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("SSH Key Name", style="blue")

    def _add_cloud_node_row(self, table: Table, node: CloudNode):
        """Add a row with all CloudNode specific attributes."""
        table.add_row(
            str(node.id),
            str(node.node_type),
            str(node.description),
            str(node.location),
            str(node.gpu_count),
            str(node.gpu_vendor),
            str(node.gpu_type),
            str(node.gpu_memory),
            str(node.cpu_cores),
            str(node.memory_gb),
            str(node.storage_gb),
            str(node.import_time),
            str(node.node_status),
            str(node.provider),
            str(node.instance_type),
            str(node.region),
            str(node.price_per_hour),
        )

    def _add_self_managed_node_row(self, table: Table, node: SelfManagedNode):
        """Add a row with all SelfManagedNode specific attributes."""
        table.add_row(
            str(node.id),
            str(node.node_type),
            str(node.description),
            str(node.location),
            str(node.gpu_count),
            str(node.gpu_vendor),
            str(node.gpu_type),
            str(node.gpu_memory),
            str(node.cpu_cores),
            str(node.memory_gb),
            str(node.storage_gb),
            str(node.import_time),
            str(node.node_status),
            str(node.endpoint),
            str(node.username),
            str(node.ssh_key_id),
        )

    def display_nodes(self, nodes: List[NodeResponse]):
        if not nodes:
            self.print_info("No nodes found. Please add nodes to the node pool.")
            return

        cloud_table = self._create_node_table("Cloud Nodes")
        self_managed_table = self._create_node_table("Self-Managed Nodes")

        self._add_common_columns(cloud_table)
        self._add_common_columns(self_managed_table)
        self._add_cloud_node_specific_columns(cloud_table)
        self._add_self_managed_node_specific_columns(self_managed_table)

        for node in nodes:
            if isinstance(node.actual_instance, CloudNode):
                self._add_cloud_node_row(cloud_table, node.actual_instance)
            elif isinstance(node.actual_instance, SelfManagedNode):
                self._add_self_managed_node_row(
                    self_managed_table, node.actual_instance
                )

        if any(isinstance(node.actual_instance, CloudNode) for node in nodes):
            self.console.print(cloud_table)
        if any(isinstance(node.actual_instance, SelfManagedNode) for node in nodes):
            self.console.print(self_managed_table)

    def display_node(self, node: NodeResponse):
        """Display a single node with all its attributes."""
        if isinstance(node.actual_instance, CloudNode):
            table = self._create_node_table("Cloud Node Details")
            self._add_common_columns(table)
            self._add_cloud_node_specific_columns(table)
            self._add_cloud_node_row(table, node.actual_instance)
        elif isinstance(node.actual_instance, SelfManagedNode):
            table = self._create_node_table("Self-Managed Node Details")
            self._add_common_columns(table)
            self._add_self_managed_node_specific_columns(table)
            self._add_self_managed_node_row(table, node.actual_instance)
        self.console.print(table)

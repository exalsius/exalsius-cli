from typing import List

from exalsius_api_client.models.base_node import BaseNode
from rich.console import Console
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class NodeDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_nodes(self, nodes: List[BaseNode]):
        if not nodes:
            self.print_info("No nodes found. Please add nodes to the node pool.")
            return

        table = Table(
            title="Nodes", show_header=True, header_style="bold", border_style="custom"
        )

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

        for node in nodes:
            table.add_row(
                node.id,
                node.node_type,
                node.description,
                node.location,
                node.gpu_count,
                node.gpu_vendor,
                node.gpu_type,
                node.gpu_memory,
                node.cpu_cores,
                node.memory_gb,
                node.storage_gb,
                node.import_time,
                node.node_status,
            )

        self.console.print(table)

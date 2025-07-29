from typing import List

from exalsius_api_client.models.cluster_template import ClusterTemplate
from rich.console import Console
from rich.table import Table

from exalsius.base.display import BaseDisplayManager


class ClusterTemplatesDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_cluster_templates(self, cluster_templates: List[ClusterTemplate]):
        if not cluster_templates:
            self.print_info("No cluster templates found")
            return

        table = Table(
            title="Available Cluster Templates",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("Name", style="green")
        table.add_column("Description", style="cyan")
        table.add_column("Kubernetes Version", style="magenta")

        for cluster_template in cluster_templates:
            table.add_row(
                cluster_template.name,
                cluster_template.description,
                cluster_template.k8s_version,
            )

        self.console.print(table)

from typing import List

from exalsius_api_client.models.credentials import Credentials
from rich.console import Console
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class CloudCredentialsDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

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

from typing import List

from exalsius_api_client.models.ssh_key import SshKey
from rich.console import Console
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class SSHKeyDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_ssh_keys(self, ssh_keys: List[SshKey]):
        if not ssh_keys:
            self.print_info("No SSH keys found")
            return

        table = Table(
            title="Available SSH Keys",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")

        for ssh_key in ssh_keys:
            table.add_row(ssh_key.id, ssh_key.name)

        self.console.print(table)

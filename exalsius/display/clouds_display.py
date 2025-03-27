from rich.console import Console
from rich.table import Table
from sky.clouds.cloud import Cloud


class CloudDisplayManager:
    def __init__(self, console: Console):
        self.console = console

    def display_cloud_list(self, clouds: list[Cloud]) -> None:
        """
        Display the list of clouds in a formatted table.

        Args:
            clouds (List[Dict[str, str]]): List of cloud providers with their status
        """
        table = Table(
            title="Cloud Providers",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Enabled", style="magenta")
        table.add_column("Egress cost\n(10GB/month)", style="cyan")

        for cloud in clouds:
            status, reason = cloud.check_credentials()
            table.add_row(cloud._REPR, str(status), str(cloud.get_egress_cost(10)))

        self.console.print(table)

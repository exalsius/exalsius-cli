from exalsius_api_client.models.offers_list_response import OffersListResponse
from rich.console import Console
from rich.table import Table


class ScanPricesDisplayManager:
    def __init__(self, console: Console):
        self.console = console

    def display_accelerator_prices(self, offers_list: OffersListResponse) -> None:
        """
        Display the accelerator prices in a formatted table.

        Args:
            offers_list (OffersListResponse): The list of offers to display
        """
        offers_by_gpu = {}
        for offer in offers_list.offers:
            if offer.gpu_type not in offers_by_gpu:
                offers_by_gpu[offer.gpu_type] = []
            offers_by_gpu[offer.gpu_type].append(offer)

        for gpu_type, offers in offers_by_gpu.items():
            offers.sort(
                key=lambda x: (
                    x.hourly_cost if x.hourly_cost is not None else float("inf")
                )
            )

            table = Table(
                title=gpu_type,
                show_header=True,
                header_style="bold",
                border_style="custom",
            )

            table.add_column("GPU", style="cyan")
            table.add_column("QTY", style="green")
            table.add_column("CLOUD", style="magenta")
            table.add_column("INSTANCE TYPE", style="blue")
            table.add_column("GPU MEM (MiB)", style="yellow")
            table.add_column("vCPUs", style="green")
            table.add_column("HOST MEM (MiB)", style="yellow")
            table.add_column("HOURLY COST", style="red")
            table.add_column("REGION", style="cyan")

            for offer in offers:
                table.add_row(
                    str(offer.gpu_type),
                    str(offer.gpu_count),
                    str(offer.cloud_provider),
                    str(offer.instance_type),
                    (
                        f"{offer.gpu_memory_mib:,}"
                        if offer.gpu_memory_mib is not None
                        else "-"
                    ),
                    str(offer.num_vcpus) if offer.num_vcpus is not None else "-",
                    (
                        f"{offer.main_memory_mib:,}"
                        if offer.main_memory_mib is not None
                        else "-"
                    ),
                    (
                        f"$ {offer.hourly_cost:.3f}"
                        if offer.hourly_cost is not None
                        else "-"
                    ),
                    str(offer.region),
                )

            self.console.print(table)

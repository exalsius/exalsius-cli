from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import exalsius_api_client
import pandas as pd
import typer
from exalsius_api_client.models.offers_list_response import OffersListResponse

# TODO: use an env variable instead of the hardcoded value
configuration = exalsius_api_client.Configuration(host="http://localhost:5000")


class ScanPricesOperation(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass


class ListAcceleratorsOperation(ScanPricesOperation):
    def __init__(
        self,
        gpu: Optional[str] = None,
        quantity: Optional[int] = None,
        region: Optional[str] = None,
        clouds: Optional[list[str]] = None,
        all_clouds: bool = False,
    ):
        self.gpu = gpu
        self.quantity = quantity
        self.region = region
        self.clouds = clouds
        self.all_clouds = all_clouds

    def execute(self) -> Dict[str, pd.DataFrame]:
        """
        Execute the list accelerators operation.

        Returns:
            dict[str, pd.DataFrame]: Dictionary mapping GPU names to their price data
        """
        with exalsius_api_client.ApiClient(configuration) as api_client:
            api_instance = exalsius_api_client.OffersApi(api_client)

            try:
                offers_list: OffersListResponse = api_instance.get_offers(
                    gpu_vendor=self.gpu,
                    gpu_type=self.gpu,
                    cloud_provider=self.clouds,
                    region=self.region,
                    gpu_count=self.quantity,
                )
            except Exception as e:
                self.console.print(f"[red]Error listing accelerators: {str(e)}[/red]")
                raise typer.Exit(1)

        return offers_list

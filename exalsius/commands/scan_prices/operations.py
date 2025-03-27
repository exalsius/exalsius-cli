from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd
import typer
from sky.client import sdk
from sky.exceptions import ApiServerConnectionError

from exalsius.services.clouds_service import CloudService
from exalsius.utils.price_utils import process_accelerator_data


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
        self.cloud_service = CloudService()

    def execute(self) -> Dict[str, pd.DataFrame]:
        """
        Execute the list accelerators operation.

        Returns:
            dict[str, pd.DataFrame]: Dictionary mapping GPU names to their price data
        """
        if not self.all_clouds and self.clouds is None:
            self.clouds = self.cloud_service.get_enabled_clouds()

        try:
            result = sdk.stream_and_get(
                sdk.list_accelerators(
                    gpus_only=True,
                    name_filter=self.gpu,
                    quantity_filter=self.quantity,
                    region_filter=self.region,
                    all_regions=not bool(self.region),
                    clouds=self.clouds if not self.all_clouds else None,
                    case_sensitive=False,
                )
            )
        except ApiServerConnectionError as e:
            self.console.print(f"[red]Error listing accelerators: {str(e)}[/red]")
            raise typer.Exit(1)

        return process_accelerator_data(result)

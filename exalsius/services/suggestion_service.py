from typing import Optional

import pandas as pd
from rich.console import Console
from sky.client import sdk

from exalsius.services.clouds_service import CloudService
from exalsius.utils.price_utils import _sort_by_cheapest


class SuggestionService:
    def __init__(self):
        self.cloud_service = CloudService()

    def get_instance_options(
        self,
        console: Console,
        gpu_types: list[str],
        parallelism: int,
    ) -> Optional[pd.DataFrame]:
        """Get and process available instance options, suggesting the best matches based on GPU types."""
        enabled_clouds = self.cloud_service.get_enabled_clouds()
        # console.print(f"Enabled clouds: {enabled_clouds}", style="custom")

        all_instances = {}
        for gpu in gpu_types:
            result = sdk.stream_and_get(
                sdk.list_accelerators(
                    gpus_only=True,
                    name_filter=gpu,
                    all_regions=True,
                    clouds=enabled_clouds,
                    case_sensitive=False,
                )
            )
            if gpu in result:
                all_instances[gpu] = result[gpu]
            else:
                console.print(f"No instances found for GPU {gpu}", style="custom")

        processed_data = _sort_by_cheapest(all_instances)
        return processed_data

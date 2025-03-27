import pandas as pd
from rich.console import Console

from exalsius.display.common import display_rich_table


class ScanPricesDisplayManager:
    def __init__(self, console: Console):
        self.console = console

    def display_accelerator_prices(
        self, processed_data: dict[str, pd.DataFrame]
    ) -> None:
        """
        Display the accelerator prices in a formatted table.

        Args:
            processed_data (dict[str, pd.DataFrame]): Dictionary mapping GPU names to their price data
        """
        for gpu_name, df in processed_data.items():
            table = display_rich_table(df, gpu_name)
            self.console.print(table)

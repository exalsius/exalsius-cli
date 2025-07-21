from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from exalsius.display.common import display_rich_table


class JobDisplayManager:
    def __init__(self, console: Console):
        self.console = console

    def display_jobs(self, jobs: List[Dict]):
        """Display a list of jobs in a formatted table."""
        table = Table(
            title="exalsius Training Jobs",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Colony", style="green")
        table.add_column("Creation Time", style="green")
        table.add_column("Image", style="blue")
        table.add_column("Script Path", style="blue")
        table.add_column("Parallelism", style="green")
        table.add_column("GPUs per Node", style="green")

        for job in jobs:
            metadata = job.get("metadata", {})
            name = metadata.get("name", "unknown")
            colony = job.get("spec", {}).get(
                "targetColony", "exalsius Management Cluster"
            )
            image = job.get("spec", {}).get("image", "unknown")
            script_path = job.get("spec", {}).get("scriptPath", "unknown")
            parallelism = job.get("spec", {}).get("parallelism", "unknown")
            gpus_per_node = job.get("spec", {}).get("nprocPerNode", "unknown")

            status = job.get("status", {}).get("phase", "unknown")
            creation = metadata.get("creationTimestamp", "N/A")

            table.add_row(
                name,
                str(status),
                colony,
                creation,
                image,
                script_path,
                str(parallelism),
                str(gpus_per_node),
            )

        self.console.print(table)

    def display_options_and_get_choice(
        self,
        data_df: pd.DataFrame,
        top_n: int,
        gpu_types: list[str],
    ) -> Optional[Dict]:
        """Display options and get user choice."""
        if data_df is None or data_df.empty:
            return None

        if top_n:
            data_df = data_df.head(top_n)
        # Fix: Convert range to a list so pandas can insert it as a column
        data_df.insert(0, "id", np.arange(1, 1 + len(data_df)))

        table = display_rich_table(
            data_df,
            f"Top {top_n} cheapest options for {gpu_types} in enabled clouds:",
            id_column=True,
        )

        self.console.print(table)

        try:
            choice = self.console.input(
                "[custom]Please select an option by entering its ID: [/custom]"
            )
            choice_id = int(choice)
            matching_rows = data_df[data_df["id"] == choice_id]

            if matching_rows.empty:
                return None

            return matching_rows.iloc[0].to_dict()
        except (ValueError, IndexError):
            return None

    def display_configuration(
        self,
        cloud: str,
        instance_type: str,
        region: str,
        price: float,
        parallelism: int,
    ):
        self.console.print("[info]Selected configuration:[/info]", style="custom")
        self.console.print(f"• Cloud: {cloud}", style="custom")
        self.console.print(f"• Instance Type: {instance_type}", style="custom")
        self.console.print(f"• Region: {region}", style="custom")
        self.console.print(f"• Parallelism: {parallelism}", style="custom")
        self.console.print(
            f"• Total cost: ${price * parallelism:.2f}/hour", style="custom"
        )

        if not typer.confirm("Do you want to proceed?"):
            self.console.print("[info]Operation cancelled[/info]")
            raise typer.Exit(0)

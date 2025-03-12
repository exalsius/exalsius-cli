from typing import Dict, List, Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from sky.client import sdk

from exalsius.commands.clouds import _list_enabled_clouds

app = typer.Typer()

custom_theme = Theme(
    {
        "custom": "#f46907",
    }
)


def process_accelerator_data(result: Dict) -> Dict[str, pd.DataFrame]:
    """Process the raw accelerator data into sorted DataFrames"""
    processed_data = {}

    for gpu, items in result.items():
        # Convert list of InstanceTypeInfo to DataFrame
        df = pd.DataFrame([t._asdict() for t in items])

        # Calculate minimum prices and sort
        df = (
            df.assign(
                min_price=df.groupby("cloud")["price"].transform("min"),
                min_spot_price=df.groupby("cloud")["spot_price"].transform("min"),
            )
            .sort_values(
                by=["min_price", "min_spot_price", "cloud", "price", "spot_price"]
            )
            .drop(columns=["min_price", "min_spot_price"])
        )

        processed_data[gpu] = df

    return processed_data


def create_rich_table(df: pd.DataFrame, title: str, id_column: bool = False) -> Table:
    """Create a Rich table from processed DataFrame"""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        border_style="custom",
    )

    id_field_col = ["id", "ID"]

    columns = [
        ("accelerator_name", "GPU"),
        ("accelerator_count", "QTY"),
        ("cloud", "CLOUD"),
        ("instance_type", "INSTANCE_TYPE"),
        ("device_memory", "DEVICE_MEM"),
        ("cpu_count", "vCPUs"),
        ("memory", "HOST_MEM"),
        ("price", "HOURLY_PRICE"),
        ("spot_price", "HOURLY_SPOT_PRICE"),
        ("region", "REGION"),
    ]

    if id_column:
        columns.insert(0, id_field_col)

    for _, header in columns:
        table.add_column(header)

    for _, row in df.iterrows():
        formatted_row = [
            str(row["accelerator_name"]),
            str(row["accelerator_count"]),
            str(row["cloud"]),
            (
                str(row["instance_type"])
                if not pd.isna(row["instance_type"])
                else "(attachable)"
            ),
            (
                f"{row['device_memory']:.0f}GB"
                if not pd.isna(row["device_memory"])
                else "-"
            ),
            (
                str(int(row["cpu_count"]))
                if not pd.isna(row["cpu_count"])
                and float(row["cpu_count"]).is_integer()
                else f"{row['cpu_count']:.1f}" if not pd.isna(row["cpu_count"]) else "-"
            ),
            f"{row['memory']:.0f}GB" if not pd.isna(row["memory"]) else "-",
            f"$ {row['price']:.3f}" if not pd.isna(row["price"]) else "-",
            f"$ {row['spot_price']:.3f}" if not pd.isna(row["spot_price"]) else "-",
            str(row["region"]) if not pd.isna(row["region"]) else "-",
        ]
        if id_column:
            formatted_row.insert(0, str(row["id"]))
        table.add_row(*formatted_row)

    return table


def parse_clouds(value: Optional[List[str]]) -> Optional[List[str]]:
    if not value:
        return None
    if len(value) == 1 and "," in value[0]:
        return [item.strip() for item in value[0].split(",")]
    return value


@app.command("list-gpus")
def list_available_accelerators(
    gpu: Optional[str] = typer.Option(
        None, "--gpu", help="Filter GPUs by name, e.g. 'H100'"
    ),
    quantity: Optional[int] = typer.Option(
        None, "--quantity", help="Minimum number of GPUs required"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", help="Filter by specific region"
    ),
    clouds: Optional[List[str]] = typer.Option(
        None,
        "--clouds",
        help="List of clouds to search (multiple flags allowed). If not provided, all enabled clouds will be searched.",
    ),
    all_clouds: Optional[bool] = typer.Option(
        False, "--all-clouds", help="Search all public clouds"
    ),
) -> None:
    """
    List available accelerator instances in public and configured clouds.
    """
    console = Console(theme=custom_theme)
    with console.status(
        "[bold custom]Scanning for prices...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        if not all_clouds and clouds is None:
            clouds = _list_enabled_clouds()

        # Get accelerator data
        result = sdk.stream_and_get(
            sdk.list_accelerators(
                gpus_only=True,
                name_filter=gpu,
                quantity_filter=quantity,
                region_filter=region,
                all_regions=not bool(region),
                clouds=clouds if not all_clouds else None,
                case_sensitive=False,
            )
        )

        # Process data and create tables
        processed_data = process_accelerator_data(result)

    for gpu_name, df in processed_data.items():
        table = create_rich_table(df, gpu_name)
        console.print(table)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    Scan and search for GPU prices across cloud providers
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

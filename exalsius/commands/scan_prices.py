from typing import Optional

import typer
from rich.console import Console
from sky.client import sdk

from exalsius.commands.clouds import _list_enabled_clouds
from exalsius.utils.cli_utils import create_rich_table
from exalsius.utils.price_utils import process_accelerator_data
from exalsius.utils.theme import custom_theme

app = typer.Typer()


def parse_clouds(value: Optional[list[str]]) -> Optional[list[str]]:
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
    clouds: Optional[list[str]] = typer.Option(
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

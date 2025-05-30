from typing import Optional

import typer
from exalsius_api_client.models.offers_list_response import OffersListResponse
from rich.console import Console

from exalsius.commands.scan_prices.operations import ListAcceleratorsOperation
from exalsius.display.scan_prices_display import ScanPricesDisplayManager
from exalsius.services.scan_prices_service import ScanPricesService
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
    service = ScanPricesService()
    display_manager = ScanPricesDisplayManager(console)

    with console.status(
        "[bold custom]Scanning for prices...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        operation = ListAcceleratorsOperation(
            gpu=gpu,
            quantity=quantity,
            region=region,
            clouds=parse_clouds(clouds),
            all_clouds=all_clouds,
        )
        offers_list: OffersListResponse = service.execute_operation(operation)

    display_manager.display_accelerator_prices(offers_list)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    Scan and search for GPU prices across cloud providers
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

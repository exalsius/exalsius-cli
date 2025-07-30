from typing import List, Optional

import typer
from exalsius_api_client.models.offers_list_response import OffersListResponse
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.offers.display import OffersDisplayManager
from exalsius.offers.service import OffersService
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    List and manage GPU offers from cloud providers.
    """
    utils.help_if_no_subcommand(ctx)


def parse_clouds(value: Optional[List[str]]) -> Optional[List[str]]:
    if not value:
        return None
    if len(value) == 1 and "," in value[0]:
        return [item.strip() for item in value[0].split(",")]
    return value


@app.command("list")
def list_offers(
    ctx: typer.Context,
    gpu_type: Optional[str] = typer.Option(
        None, "--gpu-type", help="Filter GPUs by name, e.g. 'H100'"
    ),
    gpu_vendor: Optional[str] = typer.Option(
        None, "--gpu-vendor", help="Filter GPUs by vendor, e.g. 'NVIDIA'"
    ),
    cloud_provider: Optional[str] = typer.Option(
        None, "--cloud-provider", help="Filter offers by cloud provider"
    ),
    price_min: Optional[float] = typer.Option(
        None, "--price-min", help="Minimum price per hour"
    ),
    price_max: Optional[float] = typer.Option(
        None, "--price-max", help="Maximum price per hour"
    ),
) -> None:
    """
    List available GPU offers from cloud providers.
    """
    console = Console(theme=custom_theme)
    display_manager = OffersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = OffersService(config, access_token)

    with console.status(
        "[bold custom]Fetching offers...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        try:
            offers_response: OffersListResponse = service.list_offers(
                gpu_type=gpu_type,
                gpu_vendor=gpu_vendor,
                cloud_provider=cloud_provider,
                price_min=price_min,
                price_max=price_max,
            )
        except Exception as e:
            display_manager.print_error(f"Failed to fetch offers: {e}")
            raise typer.Exit(1)

    display_manager.display_offers(offers_response.offers)

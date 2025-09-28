from typing import List, Optional

import typer
from exalsius_api_client.models.offer import Offer

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.offers.display import TableOffersDisplayManager
from exalsius.offers.service import OffersService
from exalsius.utils import commons as utils

offers_app = typer.Typer()


@offers_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
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


@offers_app.command("list")
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
    display_manager: TableOffersDisplayManager = TableOffersDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)

    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = OffersService(config, access_token)

    try:
        offers: List[Offer] = service.list_offers(
            gpu_type=gpu_type,
            gpu_vendor=gpu_vendor,
            cloud_provider=cloud_provider,
            price_min=price_min,
            price_max=price_max,
        )
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)

    display_manager.display_offers(offers)

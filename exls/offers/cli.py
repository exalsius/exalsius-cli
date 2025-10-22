from typing import List, Optional

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.offers.display import TableOffersDisplayManager
from exls.offers.dtos import OfferDTO, OffersListRequestDTO
from exls.offers.service import OffersService, get_offers_service
from exls.utils import commons as utils

offers_app = typer.Typer()


def _get_offers_service(ctx: typer.Context) -> OffersService:
    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    return get_offers_service(config, access_token)


@offers_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    List and manage GPU offers from cloud providers.
    """
    utils.help_if_no_subcommand(ctx)


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

    service: OffersService = _get_offers_service(ctx)

    try:
        offers: List[OfferDTO] = service.list_offers(
            OffersListRequestDTO(
                gpu_type=gpu_type,
                gpu_vendor=gpu_vendor,
                cloud_provider=cloud_provider,
                price_min=price_min,
                price_max=price_max,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_offers(offers)

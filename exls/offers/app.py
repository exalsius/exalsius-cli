from typing import List, Optional

import typer

from exls.offers.adapters.bundle import OffersBundle
from exls.offers.adapters.dtos import OfferDTO
from exls.offers.adapters.ui.display.display import OffersInteractionManager
from exls.offers.adapters.ui.mappers import offer_dto_from_domain
from exls.offers.core.domain import Offer
from exls.offers.core.requests import OffersFilterCriteria
from exls.offers.core.service import OffersService
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.service import ServiceError

offers_app = typer.Typer()


@offers_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    List and manage GPU offers from cloud providers.
    """
    help_if_no_subcommand(ctx)


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
    bundle: OffersBundle = OffersBundle(ctx)
    service: OffersService = bundle.get_offers_service()
    display_manager: OffersInteractionManager = bundle.get_interaction_manager()

    try:
        domain_offers: List[Offer] = service.list_offers(
            OffersFilterCriteria(
                gpu_type=gpu_type,
                gpu_vendor=gpu_vendor,
                cloud_provider=cloud_provider,
                price_min=price_min,
                price_max=price_max,
            )
        )
        offers: List[OfferDTO] = [
            offer_dto_from_domain(offer) for offer in domain_offers
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(offers, output_format=bundle.object_output_format)

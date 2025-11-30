import typer

from exls.offers.adapters.gateway.sdk import create_offers_gateway
from exls.offers.adapters.ui.display.display import IOOffersFacade
from exls.offers.core.ports import IOffersGateway
from exls.offers.core.service import OffersService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory


class OffersBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_offers_service(self) -> OffersService:
        offers_gateway: IOffersGateway = create_offers_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        return OffersService(offers_gateway)

    def get_io_facade(self) -> IOOffersFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOOffersFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

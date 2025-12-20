import typer
from exalsius_api_client.api.offers_api import OffersApi

from exls.offers.adapters.gateway.gateway import OffersGateway
from exls.offers.adapters.gateway.sdk.sdk import OffersGatewaySdk
from exls.offers.core.service import OffersService
from exls.shared.adapters.bundle import BaseBundle


class OffersBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_offers_service(self) -> OffersService:
        offers_api: OffersApi = OffersApi(api_client=self.create_api_client())
        offers_gateway: OffersGateway = OffersGatewaySdk(offers_api=offers_api)
        return OffersService(offers_repository=offers_gateway)

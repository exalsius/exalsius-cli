from typing import List

from exalsius.config import AppConfig
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.offers.domain import Offer, OfferFilterParams
from exalsius.offers.dtos import OfferDTO, OffersListRequestDTO
from exalsius.offers.gateway.base import OffersGateway


class OffersService:
    def __init__(self, offers_gateway: OffersGateway):
        self.offers_gateway: OffersGateway = offers_gateway

    def _sanity_filter_offers(self, offers: List[Offer]) -> List[Offer]:
        filtered_offers: List[Offer] = [
            offer for offer in offers if offer.price_per_hour > 0.0
        ]
        return filtered_offers

    @handle_service_errors("listing offers")
    def list_offers(self, request: OffersListRequestDTO) -> List[OfferDTO]:
        offer_filter_params: OfferFilterParams = OfferFilterParams(
            gpu_type=request.gpu_type,
            gpu_vendor=request.gpu_vendor,
            cloud_provider=request.cloud_provider,
            price_min=request.price_min,
            price_max=request.price_max,
        )
        offers: List[Offer] = self.offers_gateway.list(offer_filter_params)
        offers = self._sanity_filter_offers(offers)
        return [OfferDTO.from_domain(offer) for offer in offers]


def get_offers_service(config: AppConfig, access_token: str) -> OffersService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    offers_gateway: OffersGateway = gateway_factory.create_offers_gateway()
    return OffersService(offers_gateway=offers_gateway)

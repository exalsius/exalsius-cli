from typing import List

from exls.offers.core.domain import Offer
from exls.offers.core.ports import IOffersGateway
from exls.offers.core.requests import OffersFilterCriteria
from exls.shared.adapters.decorators import handle_service_layer_errors


class OffersService:
    def __init__(self, offers_gateway: IOffersGateway):
        self.offers_gateway: IOffersGateway = offers_gateway

    def _sanity_filter_offers(self, offers: List[Offer]) -> List[Offer]:
        filtered_offers: List[Offer] = [
            offer for offer in offers if offer.price_per_hour > 0.0
        ]
        return filtered_offers

    @handle_service_layer_errors("listing offers")
    def list_offers(self, request: OffersFilterCriteria) -> List[Offer]:
        offers: List[Offer] = self.offers_gateway.list(request)
        offers = self._sanity_filter_offers(offers)
        return offers

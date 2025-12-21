from typing import List

from exls.offers.core.domain import Offer
from exls.offers.core.ports.repository import OffersRepository
from exls.offers.core.requests import OffersFilterCriteria
from exls.shared.core.decorators import handle_service_layer_errors


class OffersService:
    def __init__(self, offers_repository: OffersRepository):
        self._offers_repository: OffersRepository = offers_repository

    def _sanity_filter_offers(self, offers: List[Offer]) -> List[Offer]:
        filtered_offers: List[Offer] = [
            offer for offer in offers if offer.price_per_hour > 0.0
        ]
        return filtered_offers

    @handle_service_layer_errors("listing offers")
    def list_offers(self, request: OffersFilterCriteria) -> List[Offer]:
        offers: List[Offer] = self._offers_repository.list(request)
        offers = self._sanity_filter_offers(offers)
        return offers

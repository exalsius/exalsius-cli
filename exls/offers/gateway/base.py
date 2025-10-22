from abc import ABC, abstractmethod
from typing import List

from exls.offers.domain import Offer, OfferFilterParams


class OffersGateway(ABC):
    @abstractmethod
    def list(self, offer_filter_params: OfferFilterParams) -> List[Offer]:
        raise NotImplementedError

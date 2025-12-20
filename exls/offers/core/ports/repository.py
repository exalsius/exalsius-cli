from abc import ABC, abstractmethod
from typing import List

from exls.offers.core.domain import Offer
from exls.offers.core.requests import OffersFilterCriteria


class OffersRepository(ABC):
    @abstractmethod
    def list(self, request: OffersFilterCriteria) -> List[Offer]: ...

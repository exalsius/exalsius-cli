from typing import List

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exls.offers.domain import Offer, OfferFilterParams
from exls.offers.gateway.base import OffersGateway
from exls.offers.gateway.commands import ListOffersSdkCommand


class OffersGatewaySdk(OffersGateway):
    def __init__(self, offers_api: OffersApi):
        self._offers_api = offers_api

    def list(self, offer_filter_params: OfferFilterParams) -> List[Offer]:
        command = ListOffersSdkCommand(self._offers_api, offer_filter_params)
        response: OffersListResponse = command.execute()
        return [Offer(sdk_model=sdk_offer) for sdk_offer in response.offers]

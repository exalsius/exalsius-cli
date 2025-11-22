from typing import List

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exls.offers.adapters.gateway.commands import ListOffersSdkCommand
from exls.offers.adapters.gateway.mappers import offer_from_sdk
from exls.offers.core.domain import Offer
from exls.offers.core.ports import IOffersGateway
from exls.offers.core.requests import OffersFilterCriteria
from exls.shared.adapters.gateway.sdk.service import create_api_client


class OffersGatewaySdk(IOffersGateway):
    def __init__(self, offers_api: OffersApi):
        self._offers_api = offers_api

    def list(self, request: OffersFilterCriteria) -> List[Offer]:
        command = ListOffersSdkCommand(self._offers_api, request)
        response: OffersListResponse = command.execute()
        return [offer_from_sdk(sdk_offer) for sdk_offer in response.offers]


def create_offers_gateway(backend_host: str, access_token: str) -> IOffersGateway:
    offers_api: OffersApi = OffersApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return OffersGatewaySdk(offers_api=offers_api)

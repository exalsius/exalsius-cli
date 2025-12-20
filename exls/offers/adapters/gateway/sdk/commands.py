from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exls.offers.core.requests import OffersFilterCriteria
from exls.shared.adapters.sdk.command import ExalsiusSdkCommand


class BaseOffersSdkCommand[T_Cmd_Return](ExalsiusSdkCommand[OffersApi, T_Cmd_Return]):
    """Base class for all offers commands. Fixes the generic API type to OffersApi."""

    pass


class ListOffersSdkCommand(BaseOffersSdkCommand[OffersListResponse]):
    """Command to list offers."""

    def __init__(self, api_client: OffersApi, request: OffersFilterCriteria):
        super().__init__(api_client)

        self._request: OffersFilterCriteria = request

    def _execute_api_call(self) -> OffersListResponse:
        response: OffersListResponse = self.api_client.get_offers(
            gpu_vendor=self._request.gpu_vendor,
            gpu_type=self._request.gpu_type,
            cloud_provider=self._request.cloud_provider,
            price_min=self._request.price_min,
            price_max=self._request.price_max,
        )
        return response

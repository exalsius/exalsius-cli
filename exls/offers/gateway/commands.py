from typing import Optional

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exls.core.commons.gateways.commands.sdk import ExalsiusSdkCommand
from exls.offers.domain import OfferFilterParams


class BaseOffersSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[OffersApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all offers commands. Fixes the generic API type to OffersApi."""

    pass


class ListOffersSdkCommand(BaseOffersSdkCommand[OfferFilterParams, OffersListResponse]):
    """Command to list offers."""

    def _execute_api_call(
        self, params: Optional[OfferFilterParams]
    ) -> OffersListResponse:
        assert params is not None
        response: OffersListResponse = self.api_client.get_offers(
            gpu_vendor=params.gpu_vendor,
            gpu_type=params.gpu_type,
            cloud_provider=params.cloud_provider,
            price_min=params.price_min,
            price_max=params.price_max,
        )
        return response

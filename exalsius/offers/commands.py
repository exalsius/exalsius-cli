from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.offers.models import OffersListRequestDTO


class ListOffersCommand(
    ExalsiusAPICommand[OffersApi, OffersListRequestDTO, OffersListResponse]
):
    def _execute_api_call(self) -> OffersListResponse:
        return self.api_client.get_offers(
            gpu_vendor=self.request.gpu_vendor,
            gpu_type=self.request.gpu_type,
            cloud_provider=self.request.cloud_provider,
            price_min=self.request.price_min,
            price_max=self.request.price_max,
        )

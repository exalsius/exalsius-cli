from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.offers.models import OffersListRequestDTO


class ListOffersCommand(BaseCommand):
    def __init__(
        self,
        request: OffersListRequestDTO,
    ):
        self.request: OffersListRequestDTO = request

    def execute(self) -> OffersListResponse:
        return self.request.api.get_offers(
            gpu_vendor=self.request.gpu_vendor,
            gpu_type=self.request.gpu_type,
            cloud_provider=self.request.cloud_provider,
            price_min=self.request.price_min,
            price_max=self.request.price_max,
        )

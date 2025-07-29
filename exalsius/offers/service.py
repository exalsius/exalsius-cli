from typing import Optional

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.offers.commands import ListOffersCommand
from exalsius.offers.models import OffersListRequestDTO


class OffersService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.offers_api: OffersApi = OffersApi(self.api_client)

    def list_offers(
        self,
        gpu_type: Optional[str] = None,
        gpu_vendor: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
    ) -> OffersListResponse:
        return self.execute_command(
            ListOffersCommand(
                OffersListRequestDTO(
                    api=self.offers_api,
                    gpu_type=gpu_type,
                    gpu_vendor=gpu_vendor,
                    cloud_provider=cloud_provider,
                    price_min=price_min,
                    price_max=price_max,
                )
            )
        )

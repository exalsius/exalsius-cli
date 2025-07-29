from typing import Optional, Tuple

from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.base.service import BaseServiceWithAuth
from exalsius.offers.operations import ListOffersOperation


class OffersService(BaseServiceWithAuth):
    def list_offers(
        self,
        gpu_type: Optional[str] = None,
        quantity: Optional[int] = None,
        region: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        all_clouds: bool = False,
    ) -> Tuple[Optional[OffersListResponse], Optional[str]]:
        return self.execute_operation(
            ListOffersOperation(
                self.api_client,
                gpu_type=gpu_type,
                quantity=quantity,
                region=region,
                cloud_provider=cloud_provider,
                all_clouds=all_clouds,
            )
        )

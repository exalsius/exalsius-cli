from typing import List, Optional, Tuple

import exalsius_api_client
from exalsius_api_client.models.offer import Offer
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.core.operations.base import ListOperation


class ListOffersOperation(ListOperation[Offer]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        gpu_type: Optional[str] = None,
        quantity: Optional[int] = None,
        region: Optional[str] = None,
        clouds: Optional[List[str]] = None,
        all_clouds: bool = False,
    ):
        self.api_client = api_client
        self.gpu_type = gpu_type
        self.quantity = quantity
        self.region = region
        self.clouds = clouds
        self.all_clouds = all_clouds

    def execute(self) -> Tuple[Optional[List[Offer]], Optional[str]]:
        api_instance = exalsius_api_client.OffersApi(self.api_client)
        try:
            offers_list_response: OffersListResponse = api_instance.get_offers(
                gpu_vendor=self.gpu_type,
                gpu_type=self.gpu_type,
                cloud_provider=self.clouds,
                region=self.region,
                gpu_count=self.quantity,
            )
        except Exception as e:
            return None, str(e)
        return offers_list_response.offers, None

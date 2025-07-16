from typing import Optional, Tuple

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.error import Error as ExalsiusError
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.core.operations.base import BaseOperation


class ListOffersOperation(BaseOperation[OffersListResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        gpu_type: Optional[str] = None,
        quantity: Optional[int] = None,
        region: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        all_clouds: bool = False,
    ):
        self.api_client = api_client
        self.gpu_type = gpu_type
        self.quantity = quantity
        self.region = region
        self.cloud_provider = cloud_provider
        self.all_clouds = all_clouds

    def execute(self) -> Tuple[Optional[OffersListResponse], Optional[str]]:
        api_instance = OffersApi(self.api_client)
        try:
            offers_list_response: OffersListResponse = api_instance.get_offers(
                gpu_vendor=self.gpu_type,
                gpu_type=self.gpu_type,
                cloud_provider=self.cloud_provider,
                region=self.region,
                gpu_count=self.quantity,
            )
            return offers_list_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)

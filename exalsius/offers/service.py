from typing import List, Optional

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.offer import Offer
from exalsius_api_client.models.offers_list_response import OffersListResponse

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.offers.commands import ListOffersCommand
from exalsius.offers.models import OffersListRequestDTO

OFFERS_API_ERROR_TYPE: str = "OffersApiError"


class OffersService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.offers_api: OffersApi = OffersApi(self.api_client)

    def _sanity_filter_offers(self, offers: List[Offer]) -> List[Offer]:
        filtered_offers = [
            offer for offer in offers if offer.price is not None and offer.price > 0
        ]
        return filtered_offers

    def list_offers(
        self,
        gpu_type: Optional[str] = None,
        gpu_vendor: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
    ) -> List[Offer]:
        req: OffersListRequestDTO = OffersListRequestDTO(
            api=self.offers_api,
            gpu_type=gpu_type,
            gpu_vendor=gpu_vendor,
            cloud_provider=cloud_provider,
            price_min=price_min,
            price_max=price_max,
        )
        command: ListOffersCommand = ListOffersCommand(request=req)
        try:
            response: OffersListResponse = self.execute_command(command)
            offers: List[Offer] = self._sanity_filter_offers(response.offers)
            return offers
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=OFFERS_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=OFFERS_API_ERROR_TYPE,
            )

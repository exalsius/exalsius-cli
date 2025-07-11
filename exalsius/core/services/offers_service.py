from typing import List, Optional, Tuple

from exalsius_api_client.models.offer import Offer

from exalsius.core.operations.offers_operations import ListOffersOperation
from exalsius.core.services.base import BaseService


class OffersService(BaseService):
    def list_offers(
        self,
        gpu_type: Optional[str] = None,
        quantity: Optional[int] = None,
        region: Optional[str] = None,
        clouds: Optional[List[str]] = None,
        all_clouds: bool = False,
    ) -> Tuple[Optional[List[Offer]], Optional[str]]:
        return self.execute_operation(
            ListOffersOperation(
                self.api_client,
                gpu_type=gpu_type,
                quantity=quantity,
                region=region,
                clouds=clouds,
                all_clouds=all_clouds,
            )
        )

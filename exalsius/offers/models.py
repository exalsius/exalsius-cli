from typing import Optional

from exalsius_api_client.api.offers_api import OffersApi
from pydantic import Field

from exalsius.core.base.models import BaseRequestDTO


class OffersBaseRequestDTO(BaseRequestDTO):
    api: OffersApi = Field(..., description="The API client")


class OffersListRequestDTO(OffersBaseRequestDTO):
    gpu_type: Optional[str] = Field(default=None, description="The type of GPU")
    gpu_vendor: Optional[str] = Field(default=None, description="The vendor of the GPU")
    cloud_provider: Optional[str] = Field(
        default=None, description="The cloud provider"
    )
    price_min: Optional[float] = Field(default=None, description="The minimum price")
    price_max: Optional[float] = Field(default=None, description="The maximum price")

from typing import Optional

from exalsius_api_client.models.offer import Offer as SdkOffer
from pydantic import BaseModel, Field, StrictFloat, StrictStr


class OfferFilterParams(BaseModel):
    """Domain object representing query parameters for offers."""

    gpu_type: Optional[str] = Field(default=None, description="The type of GPU")
    gpu_vendor: Optional[str] = Field(default=None, description="The vendor of the GPU")
    cloud_provider: Optional[str] = Field(
        default=None, description="The cloud provider"
    )
    price_min: Optional[float] = Field(default=None, description="The minimum price")
    price_max: Optional[float] = Field(default=None, description="The maximum price")


# TODO: The price stuff needs to be properly fixed / handled


class Offer(BaseModel):
    """Domain object representing an offer."""

    sdk_model: SdkOffer = Field(..., description="The SDK model of the offer")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def provider(self) -> str:
        return self.sdk_model.cloud_provider

    @property
    def instance_type(self) -> str:
        return self.sdk_model.instance_type

    @property
    def price_per_hour(self) -> StrictFloat:
        p: float = 0.0
        if self.sdk_model.price is not None:
            p = float(self.sdk_model.price)
        return p

    @property
    def gpu_type(self) -> StrictStr:
        return self.sdk_model.gpu_type

    @property
    def gpu_count(self) -> int:
        return self.sdk_model.gpu_count

    @property
    def gpu_memory_mib(self) -> int:
        return self.sdk_model.gpu_memory_mib

    @property
    def num_vcpus(self) -> int:
        return self.sdk_model.num_vcpus

    @property
    def main_memory_mib(self) -> int:
        return self.sdk_model.main_memory_mib

    @property
    def region(self) -> StrictStr:
        return self.sdk_model.region

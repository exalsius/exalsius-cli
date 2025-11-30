from typing import Optional

from pydantic import BaseModel, Field


class OffersFilterCriteria(BaseModel):
    """Domain object representing query parameters for listing offers."""

    gpu_type: Optional[str] = Field(default=None, description="The type of GPU")
    gpu_vendor: Optional[str] = Field(default=None, description="The vendor of the GPU")
    cloud_provider: Optional[str] = Field(
        default=None, description="The cloud provider"
    )
    price_min: Optional[float] = Field(default=None, description="The minimum price")
    price_max: Optional[float] = Field(default=None, description="The maximum price")

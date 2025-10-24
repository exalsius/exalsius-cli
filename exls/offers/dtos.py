from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, StrictFloat, StrictStr

from exls.offers.domain import Offer


class OffersListRequestDTO(BaseModel):
    gpu_type: Optional[str] = Field(default=None, description="The type of GPU")
    gpu_vendor: Optional[str] = Field(default=None, description="The vendor of the GPU")
    cloud_provider: Optional[str] = Field(
        default=None, description="The cloud provider"
    )
    price_min: Optional[float] = Field(default=None, description="The minimum price")
    price_max: Optional[float] = Field(default=None, description="The maximum price")


class OfferDTO(BaseModel):
    id: StrictStr
    provider: str
    instance_type: str
    price_per_hour: StrictFloat
    gpu_type: StrictStr
    gpu_count: int
    gpu_memory_mib: int
    num_vcpus: int
    main_memory_mib: int
    region: StrictStr

    @classmethod
    def from_domain(cls, domain_obj: Offer) -> OfferDTO:
        return cls(
            id=domain_obj.id,
            provider=domain_obj.provider,
            instance_type=domain_obj.instance_type,
            price_per_hour=domain_obj.price_per_hour,
            gpu_type=domain_obj.gpu_type,
            gpu_count=domain_obj.gpu_count,
            gpu_memory_mib=domain_obj.gpu_memory_mib,
            num_vcpus=domain_obj.num_vcpus,
            main_memory_mib=domain_obj.main_memory_mib,
            region=domain_obj.region,
        )

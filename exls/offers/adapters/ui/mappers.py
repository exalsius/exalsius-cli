from exls.offers.adapters.dtos import OfferDTO
from exls.offers.core.domain import Offer


def offer_dto_from_domain(offer: Offer) -> OfferDTO:
    return OfferDTO(
        id=offer.id,
        provider=offer.provider,
        instance_type=offer.instance_type,
        price_per_hour=offer.price_per_hour,
        gpu_type=offer.gpu_type,
        gpu_count=offer.gpu_count,
        gpu_memory_mib=offer.gpu_memory_mib,
        num_vcpus=offer.num_vcpus,
        main_memory_mib=offer.main_memory_mib,
        region=offer.region,
    )

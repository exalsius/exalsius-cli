from exalsius_api_client.models.offer import Offer as SdkOffer

from exls.offers.core.domain import Offer


def offer_from_sdk(sdk_offer: SdkOffer) -> Offer:
    price: float = 0.0
    if sdk_offer.price is not None:
        price = float(sdk_offer.price)

    return Offer(
        id=sdk_offer.id or "",
        provider=sdk_offer.cloud_provider or "",
        instance_type=sdk_offer.instance_type or "",
        price_per_hour=price,
        gpu_type=sdk_offer.gpu_type or "",
        gpu_count=sdk_offer.gpu_count or 0,
        gpu_memory_mib=sdk_offer.gpu_memory_mib or 0,
        num_vcpus=sdk_offer.num_vcpus or 0,
        main_memory_mib=sdk_offer.main_memory_mib or 0,
        region=sdk_offer.region or "",
    )

from typing import List

import questionary

from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.offers.dtos import OfferDTO


def ssh_key_to_questionary_choice(
    ssh_key: SshKeyDTO,
) -> questionary.Choice:
    return questionary.Choice(
        title=f"{ssh_key.name} ({ssh_key.id[:12]}...)",
        value=ssh_key.id,
    )


def ssh_keys_to_questionary_choices(
    ssh_keys: List[SshKeyDTO],
) -> List[questionary.Choice]:
    return [ssh_key_to_questionary_choice(ssh_key) for ssh_key in ssh_keys]


def offer_to_questionary_choice(
    offer: OfferDTO,
) -> questionary.Choice:
    return questionary.Choice(
        title=f"{offer.instance_type} - {offer.provider} - ${offer.price_per_hour:.2f}/hr - {offer.gpu_type} x{offer.gpu_count}",
        value=offer.id,
    )


def offers_to_questionary_choices(
    offers: List[OfferDTO],
) -> List[questionary.Choice]:
    return [offer_to_questionary_choice(offer) for offer in offers]

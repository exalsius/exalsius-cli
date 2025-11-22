from __future__ import annotations

from typing import List

import questionary
from pydantic import StrictStr

from exls.nodes.adapters.cli.display import ComposingNodeDisplayManager
from exls.nodes.adapters.cli.mappers import offers_to_questionary_choices
from exls.nodes.adapters.dtos import ImportCloudNodeRequestDTO
from exls.offers.dtos import OfferDTO
from exls.shared.adapters.cli.display import (
    non_empty_string_validator,
    positive_integer_validator,
)
from exls.shared.core.domain import generate_random_name
from exls.shared.core.exceptions import ExalsiusError
from exls.shared.core.ports import UserCancellationException


class NodeImportOfferFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive offer node import flow."""


# TODO: This wont really work since offers lists are too large and paginated.
# this requires a more complex flow that allows to handle such large lists.


class NodeImportOfferFlow:
    """Flow for cloud offer node import configuration."""

    def __init__(
        self,
        available_offers: List[OfferDTO],
        display_manager: ComposingNodeDisplayManager,
    ):
        if not available_offers:
            raise ValueError(
                "No offers available. Check your filters or try again later."
            )
        self._available_offers: List[OfferDTO] = available_offers
        self._display_manager: ComposingNodeDisplayManager = display_manager

    def run(self) -> ImportCloudNodeRequestDTO:
        """
        Collect cloud offer import details and return DTO.

        Returns:
            NodesImportFromOfferRequestDTO if successful
        """

        try:
            self._display_manager.display_info(
                "🚀 Cloud Offer Node Import - Interactive Mode: This will guide you through importing a node"
            )

            offer_choices: List[questionary.Choice] = offers_to_questionary_choices(
                self._available_offers
            )
            offer_choice: questionary.Choice = (
                self._display_manager.ask_select_required(
                    "Select offer:",
                    choices=offer_choices,
                    default=offer_choices[0],
                )
            )
            offer_id: str = str(offer_choice.value)

            amount: str = self._display_manager.ask_text(
                "Amount of nodes to import from offer:",
                default="1",
                validator=positive_integer_validator,
            )

            hostname: StrictStr = self._display_manager.ask_text(
                "Hostname - nodes will be numbered sequentially based on this hostname:",
                default=generate_random_name(prefix="node"),
                validator=non_empty_string_validator,
            )

            dto: ImportCloudNodeRequestDTO = ImportCloudNodeRequestDTO(
                hostname=hostname,
                offer_id=offer_id,
                amount=int(amount),
            )

            # TODO: This does not contain the offer details. Not optimal for the user.
            # we implement this in the future.
            self._display_manager.display_import_offer_request(dto)
            confirmed = self._display_manager.ask_confirm(
                "Import node with these settings?", default=True
            )
            if not confirmed:
                raise NodeImportOfferFlowInterruptionException(
                    "Cloud offer node import cancelled by user."
                )

        except UserCancellationException as e:
            raise NodeImportOfferFlowInterruptionException(e) from e
        except Exception as e:
            raise ExalsiusError(f"An unexpected error occurred: {str(e)}") from e

        return dto

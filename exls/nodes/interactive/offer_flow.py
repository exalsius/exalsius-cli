from typing import TYPE_CHECKING, List, Optional

import questionary
from pydantic import StrictStr

from exls.core.base.display import ErrorDisplayModel
from exls.core.commons.service import generate_random_name
from exls.nodes.dtos import NodesImportFromOfferRequestDTO
from exls.nodes.interactive.base_flow import BaseNodeImportFlow
from exls.nodes.interactive.mappers import offers_to_questionary_choices
from exls.offers.dtos import OfferDTO

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class NodeImportOfferFlow(BaseNodeImportFlow):
    """Flow for cloud offer node import configuration."""

    def __init__(
        self,
        offers: List[OfferDTO],
        display_manager: "ComposingNodeDisplayManager",
    ):
        super().__init__(display_manager)
        if not offers:
            raise ValueError(
                "No offers available. Check your filters or try again later."
            )
        self._offers: List[OfferDTO] = offers

    def run(self) -> Optional[NodesImportFromOfferRequestDTO]:
        """
        Collect cloud offer import details and return DTO.

        Returns:
            NodesImportFromOfferRequestDTO if successful, None if cancelled
        """
        try:
            self._display_manager.display_offers(self._offers)

            offer_choices: List[questionary.Choice] = offers_to_questionary_choices(
                self._offers
            )
            offer_id = self._display_manager.ask_select_required(
                "Select offer:",
                choices=offer_choices,
                default=offer_choices[0],
            )

            hostname: StrictStr = self._display_manager.ask_text(
                "Hostname:", default=generate_random_name(prefix="node")
            )

            amount: int
            while True:
                amount_str: StrictStr = self._display_manager.ask_text(
                    "Amount of nodes to import:", default="1"
                )
                try:
                    amount = int(amount_str)
                    if amount > 0:
                        break
                    else:
                        self._display_manager.display_error(
                            ErrorDisplayModel(
                                message="Please enter a positive integer."
                            )
                        )
                except ValueError:
                    self._display_manager.display_error(
                        ErrorDisplayModel(message="Please enter a valid integer.")
                    )

            dto = NodesImportFromOfferRequestDTO(
                hostname=hostname,
                offer_id=str(offer_id),
                amount=amount,
            )

            self._display_manager.display_import_offer_request(dto)
            confirmed = self._display_manager.ask_confirm(
                "Import node(s) with these settings?", default=True
            )

            if not confirmed:
                return None

            return dto

        except (KeyboardInterrupt, TypeError):
            return None

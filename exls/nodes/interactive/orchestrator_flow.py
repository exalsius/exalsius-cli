from typing import TYPE_CHECKING, List, Optional, Union

from exls.core.base.display import ErrorDisplayModel
from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.nodes.dtos import NodesImportFromOfferRequestDTO, NodesImportSSHRequestDTO
from exls.nodes.interactive.base_flow import BaseNodeImportFlow
from exls.nodes.interactive.offer_flow import NodeImportOfferFlow
from exls.nodes.interactive.selector_flow import NodeImportSelectorFlow
from exls.nodes.interactive.ssh_flow import NodeImportSSHFlow
from exls.offers.dtos import OfferDTO

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class NodeImportOrchestratorFlow(BaseNodeImportFlow):
    """Orchestrates the node import process, coordinating between sub-flows."""

    def __init__(
        self,
        ssh_keys: List[SshKeyDTO],
        offers: List[OfferDTO],
        display_manager: "ComposingNodeDisplayManager",
    ):
        super().__init__(display_manager)
        self._ssh_keys: List[SshKeyDTO] = ssh_keys
        self._offers: List[OfferDTO] = offers
        self._collected_dtos: List[
            Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]
        ] = []

    def run(
        self,
    ) -> List[Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]]:
        """
        Main orchestration method for node imports.

        Handles the import loop:
        1. User selects import type (SSH or Offer)
        2. Appropriate sub-flow collects configuration
        3. DTO is collected
        4. User can import another or exit
        5. Returns list of all collected DTOs

        Returns:
            List of import request DTOs (empty if cancelled before any imports)
        """
        try:
            self._display_manager.display_info(
                "🚀 Node Import - Interactive Mode: This will guide you through importing nodes"
            )

            while True:
                try:
                    self._display_manager.display_info("📋 Step 1: Import Type")
                    selector_flow = NodeImportSelectorFlow(self._display_manager)
                    import_type: Optional[str] = selector_flow.run()

                    if import_type is None:
                        self._display_manager.display_info(
                            "\nImport cancelled by user."
                        )
                        break

                    self._display_manager.display_info(
                        "⚙️  Step 2: Import Configuration"
                    )
                    dto: Optional[
                        Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]
                    ] = None

                    if import_type == "SSH":
                        if not self._ssh_keys:
                            self._display_manager.display_error(
                                ErrorDisplayModel(
                                    message="No SSH keys available. Please add an SSH key first using 'exls management ssh-keys add'."
                                )
                            )
                            continue
                        ssh_flow = NodeImportSSHFlow(
                            self._ssh_keys, self._display_manager
                        )
                        dto = ssh_flow.run()
                    else:  # OFFER
                        if not self._offers:
                            self._display_manager.display_error(
                                ErrorDisplayModel(
                                    message="No offers available. Try different filter values or check back later."
                                )
                            )
                            continue
                        offer_flow = NodeImportOfferFlow(
                            self._offers, self._display_manager
                        )
                        dto = offer_flow.run()

                    if dto is None:
                        continue

                    self._collected_dtos.append(dto)

                    if not self._display_manager.ask_confirm(
                        "Import another node?", default=False
                    ):
                        break

                except (KeyboardInterrupt, TypeError):
                    self._display_manager.display_info("\nImport cancelled by user.")
                    break

            if self._collected_dtos:
                self._display_manager.display_success(
                    f"\n✅ Import configuration completed! Total configurations collected: {len(self._collected_dtos)}"
                )

            return self._collected_dtos

        except (KeyboardInterrupt, TypeError):
            if self._collected_dtos:
                self._display_manager.display_info(
                    f"\nImport cancelled. {len(self._collected_dtos)} configuration(s) were collected."
                )
            return self._collected_dtos

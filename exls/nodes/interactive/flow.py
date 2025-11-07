from typing import TYPE_CHECKING, List, Optional, Union

import questionary
from pydantic import StrictStr

from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.service import generate_random_name
from exls.management.types.ssh_keys.dtos import ListSshKeysRequestDTO, SshKeyDTO
from exls.management.types.ssh_keys.service import SshKeysService
from exls.nodes.dtos import (
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
)
from exls.nodes.interactive.mappers import (
    offers_to_questionary_choices,
    ssh_keys_to_questionary_choices,
)
from exls.nodes.service import NodeService
from exls.offers.dtos import OfferDTO, OffersListRequestDTO
from exls.offers.service import OffersService

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class NodeInteractiveFlow:
    def __init__(
        self,
        node_service: NodeService,
        ssh_keys_service: SshKeysService,
        offers_service: OffersService,
        display_manager: "ComposingNodeDisplayManager",
    ):
        self._node_service: NodeService = node_service
        self._ssh_keys_service: SshKeysService = ssh_keys_service
        self._offers_service: OffersService = offers_service
        self._display_manager: "ComposingNodeDisplayManager" = display_manager
        self._session_imported_nodes: List[NodeDTO] = []

    def run(self) -> List[NodeDTO]:
        """Main orchestration method, returns list of imported node DTOs."""
        try:
            self._display_manager.display_info(
                "🚀 Node Import - Interactive Mode: This will guide you through importing nodes"
            )

            while True:
                try:
                    # Step 1: Import Type Selection
                    self._display_manager.display_info("📋 Step 1: Import Type")
                    import_type: str = self._prompt_import_type()

                    # Step 2: Collect Import Details
                    self._display_manager.display_info(
                        "⚙️  Step 2: Import Configuration"
                    )
                    import_dto: Union[
                        NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO
                    ]
                    if import_type == "SSH":
                        import_dto = self._prompt_ssh_import()
                    else:  # OFFER
                        import_dto = self._prompt_offer_import()

                    # Step 3: Summary & Confirmation
                    self._display_manager.display_info("📊 Summary")
                    if not self._display_summary(import_dto):
                        continue

                    # Step 4: Import Node
                    self._display_manager.display_info("🚀 Importing Node(s)")
                    imported_nodes: List[NodeDTO] = self._import_node(import_dto)
                    self._session_imported_nodes.extend(imported_nodes)

                    # Display success
                    if len(imported_nodes) == 1:
                        self._display_manager.display_success(
                            f"Node {imported_nodes[0].hostname} (ID: {imported_nodes[0].id}) imported successfully!"
                        )
                    else:
                        self._display_manager.display_success(
                            f"{len(imported_nodes)} nodes imported successfully!"
                        )
                        for node in imported_nodes:
                            self._display_manager.display_info(
                                f"  - {node.hostname} (ID: {node.id})"
                            )

                    # Step 5: Continue or Exit
                    if not self._display_manager.ask_confirm(
                        "Import another node?", default=False
                    ):
                        break

                except (KeyboardInterrupt, TypeError):
                    self._display_manager.display_info("\nImport cancelled by user.")
                    break

            # Final summary
            if self._session_imported_nodes:
                self._display_manager.display_success(
                    f"\n✅ Import session completed! Total nodes imported: {len(self._session_imported_nodes)}"
                )

            return self._session_imported_nodes

        except (KeyboardInterrupt, TypeError):
            if self._session_imported_nodes:
                self._display_manager.display_info(
                    f"\nImport cancelled. {len(self._session_imported_nodes)} node(s) were imported."
                )
            return self._session_imported_nodes

    def _prompt_import_type(self) -> str:
        """Ask user to choose between SSH and Cloud Offer import."""
        import_type_choices: List[questionary.Choice] = [
            questionary.Choice("Self-managed (SSH)", "SSH"),
            questionary.Choice("Cloud Offer", "OFFER"),
        ]
        import_type = self._display_manager.ask_select_required(
            "Choose import type:",
            choices=import_type_choices,
            default=import_type_choices[0],
        )
        return str(import_type)

    def _prompt_ssh_import(self) -> NodesImportSSHRequestDTO:
        """Collect SSH node import details."""
        hostname: StrictStr = self._display_manager.ask_text(
            "Hostname:", default=generate_random_name(prefix="node")
        )

        endpoint: StrictStr = self._display_manager.ask_text(
            "Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
        )

        username: StrictStr = self._display_manager.ask_text(
            "Username:", default="root"
        )

        ssh_key_id: str = self._load_and_select_ssh_key()

        return NodesImportSSHRequestDTO(
            hostname=hostname,
            endpoint=endpoint,
            username=username,
            ssh_key_id=ssh_key_id,
        )

    def _prompt_offer_import(self) -> NodesImportFromOfferRequestDTO:
        """Collect cloud offer import details."""
        offer_id: str = self._filter_and_select_offer()

        hostname: StrictStr = self._display_manager.ask_text(
            "Hostname:", default=generate_random_name(prefix="node")
        )

        # Ask for amount with validation
        while True:
            amount_str: StrictStr = self._display_manager.ask_text(
                "Amount of nodes to import:", default="1"
            )
            try:
                amount: int = int(amount_str)
                if amount > 0:
                    break
                else:
                    self._display_manager.display_error(
                        ErrorDisplayModel(message="Please enter a positive integer.")
                    )
            except ValueError:
                self._display_manager.display_error(
                    ErrorDisplayModel(message="Please enter a valid integer.")
                )

        return NodesImportFromOfferRequestDTO(
            hostname=hostname,
            offer_id=offer_id,
            amount=amount,
        )

    def _load_and_select_ssh_key(self) -> str:
        """Load SSH keys and let user select one. Returns ssh_key_id."""
        try:
            ssh_keys: List[SshKeyDTO] = self._ssh_keys_service.list_ssh_keys(
                ListSshKeysRequestDTO()
            )
        except ServiceError as e:
            self._display_manager.display_error(
                ErrorDisplayModel(message=f"Failed to load SSH keys: {str(e)}")
            )
            raise

        if not ssh_keys:
            self._display_manager.display_error(
                ErrorDisplayModel(
                    message="No SSH keys available. Please add an SSH key first using 'exls management ssh-keys add'."
                )
            )
            raise ValueError("No SSH keys available")

        self._display_manager.display_ssh_keys(ssh_keys)

        ssh_key_choices: List[questionary.Choice] = ssh_keys_to_questionary_choices(
            ssh_keys
        )
        ssh_key_id = self._display_manager.ask_select_required(
            "Select SSH key:",
            choices=ssh_key_choices,
            default=ssh_key_choices[0],
        )

        return str(ssh_key_id)

    def _filter_and_select_offer(self) -> str:
        """Allow user to filter offers and select one. Returns offer_id."""
        # Ask for optional filters
        gpu_type_str: StrictStr = self._display_manager.ask_text(
            "GPU type (optional, press Enter to skip):", default=""
        )
        gpu_type: Optional[str] = gpu_type_str if gpu_type_str else None

        cloud_provider_str: StrictStr = self._display_manager.ask_text(
            "Cloud provider (optional, press Enter to skip):", default=""
        )
        cloud_provider: Optional[str] = (
            cloud_provider_str if cloud_provider_str else None
        )

        # Load offers with filters
        try:
            offers: List[OfferDTO] = self._offers_service.list_offers(
                OffersListRequestDTO(
                    gpu_type=gpu_type,
                    cloud_provider=cloud_provider,
                )
            )
        except ServiceError as e:
            self._display_manager.display_error(
                ErrorDisplayModel(message=f"Failed to load offers: {str(e)}")
            )
            raise

        if not offers:
            self._display_manager.display_error(
                ErrorDisplayModel(
                    message="No offers found with the specified filters. Try different filter values."
                )
            )
            raise ValueError("No offers found with the specified filters")

        self._display_manager.display_offers(offers)

        offer_choices: List[questionary.Choice] = offers_to_questionary_choices(offers)
        offer_id = self._display_manager.ask_select_required(
            "Select offer:",
            choices=offer_choices,
            default=offer_choices[0],
        )

        return str(offer_id)

    def _display_summary(
        self, dto: Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]
    ) -> bool:
        """Show summary and confirm import."""
        if isinstance(dto, NodesImportSSHRequestDTO):
            self._display_manager.display_import_ssh_request(dto)
        else:
            self._display_manager.display_import_offer_request(dto)

        return self._display_manager.ask_confirm(
            "Import node(s) with these settings?", default=True
        )

    def _import_node(
        self, dto: Union[NodesImportSSHRequestDTO, NodesImportFromOfferRequestDTO]
    ) -> List[NodeDTO]:
        """Execute the node import."""
        try:
            if isinstance(dto, NodesImportSSHRequestDTO):
                node: NodeDTO = self._node_service.import_ssh_node(dto)
                return [node]
            else:
                nodes: List[NodeDTO] = self._node_service.import_from_offer(dto)
                return nodes
        except ServiceError as e:
            self._display_manager.display_error(
                ErrorDisplayModel(message=f"Import failed: {str(e)}")
            )
            raise

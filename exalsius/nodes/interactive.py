from typing import List, Optional

import questionary
from exalsius_api_client.models.offer import Offer
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.ssh_keys.service import SshKeysService
from exalsius.nodes.display import NodeInteractiveDisplay
from exalsius.nodes.service import NodeService
from exalsius.offers.service import OffersService
from exalsius.utils import commons as utils


class NodeInteractiveConfig:
    """Internal state for interactive node import."""

    def __init__(self):
        self.import_type: Optional[str] = None  # "SSH" or "OFFER"

        # SSH import fields
        self.hostname: str = ""
        self.endpoint: str = ""
        self.username: str = ""
        self.ssh_key_id: str = ""

        # Offer import fields
        self.offer_id: str = ""
        self.amount: int = 1

        # Track imported nodes
        self.imported_node_ids: List[str] = []


class NodeInteractiveFlow:
    """Interactive flow for node import."""

    def __init__(
        self,
        node_service: NodeService,
        ssh_keys_service: SshKeysService,
        offers_service: OffersService,
        display_manager: NodeInteractiveDisplay,
    ):
        self.node_service = node_service
        self.ssh_keys_service = ssh_keys_service
        self.offers_service = offers_service
        self.display_manager = display_manager
        self.config = NodeInteractiveConfig()
        self.available_ssh_keys: List[SshKeysListResponseSshKeysInner] = []
        self.available_offers: List[Offer] = []

    def run(self) -> List[str]:
        """Main orchestration method, returns list of imported node IDs."""
        self.display_manager.display_welcome(
            "🚀 Node Import - Interactive Mode",
            "This will guide you through importing a new node.\n",
        )

        while True:
            try:
                # Reset config for each import
                self.config = NodeInteractiveConfig()

                # Step 1: Import Type Selection
                self.display_manager.display_section("📋 Step 1: Import Type")
                self._prompt_import_type()

                # Step 2: Collect Import Details
                self.display_manager.display_section("⚙️  Step 2: Import Configuration")
                if self.config.import_type == "SSH":
                    self._prompt_ssh_import()
                else:  # OFFER
                    self._prompt_offer_import()

                # Step 3: Summary & Confirmation
                self.display_manager.display_section("📊 Summary")
                if not self._display_summary():
                    continue

                # Step 4: Import Node
                self.display_manager.display_section("🚀 Importing Node")
                self._import_node()

                # Step 5: Continue or Exit
                if not self._prompt_continue():
                    break
            except KeyboardInterrupt:
                self.display_manager.display_info("\nImport cancelled by user.")
                break

        # Final summary
        if self.config.imported_node_ids:
            self.display_manager.display_success(
                f"Import session completed! Total nodes imported: {len(self.config.imported_node_ids)}"
            )
            self.display_manager.display_info(
                f"Imported node IDs: {', '.join(self.config.imported_node_ids)}"
            )

        return self.config.imported_node_ids

    def _prompt_import_type(self) -> None:
        """Ask user to choose between SSH and Cloud Offer import."""
        try:
            import_type = questionary.select(
                "Choose import type:",
                choices=[
                    questionary.Choice("Self-managed (SSH)", "SSH"),
                    questionary.Choice("Cloud Offer", "OFFER"),
                ],
                default="SSH",
            ).ask()
            if import_type is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.import_type = import_type
        except KeyboardInterrupt:
            raise

    def _prompt_ssh_import(self) -> None:
        """Collect SSH node import details."""
        try:
            hostname = questionary.text(
                "Hostname:", default=utils.generate_random_name(prefix="node")
            ).ask()
            if hostname is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.hostname = hostname

            endpoint = questionary.text(
                "Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
            ).ask()
            if endpoint is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.endpoint = endpoint

            username = questionary.text("Username:", default="root").ask()
            if username is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.username = username

            # Load and display SSH keys
            self._load_ssh_keys()
            if not self.available_ssh_keys:
                self.display_manager.display_error(
                    ErrorDTO(
                        message="No SSH keys available. Please add an SSH key first."
                    )
                )
                return

            self._select_ssh_key()
        except KeyboardInterrupt:
            raise

    def _prompt_offer_import(self) -> None:
        """Collect cloud offer import details."""
        try:
            has_offer_id = questionary.confirm(
                "Do you have an offer ID?", default=False
            ).ask()
            if has_offer_id is None:
                raise KeyboardInterrupt("Import cancelled by user")

            if has_offer_id:
                offer_id = questionary.text(
                    "Offer ID:",
                ).ask()
                if offer_id is None:
                    raise KeyboardInterrupt("Import cancelled by user")
                self.config.offer_id = offer_id
            else:
                self._select_or_filter_offer()

            hostname = questionary.text(
                "Hostname:", default=utils.generate_random_name(prefix="node")
            ).ask()
            if hostname is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.hostname = hostname

            amount_str = questionary.text(
                "Amount of nodes to import:", default="1"
            ).ask()
            if amount_str is None:
                raise KeyboardInterrupt("Import cancelled by user")

            self.config.amount = int(amount_str)
        except KeyboardInterrupt:
            raise

    def _load_ssh_keys(self) -> None:
        """Load available SSH keys."""
        try:
            self.available_ssh_keys = self.ssh_keys_service.list_ssh_keys()
        except ServiceError as e:
            self.display_manager.display_error(
                ErrorDTO(
                    message=e.message,
                    error_type=e.error_type,
                    error_code=e.error_code,
                )
            )
            self.available_ssh_keys = []

    def _select_ssh_key(self) -> None:
        """Display SSH keys and let user select one."""
        if not self.available_ssh_keys:
            return

        self.display_manager.display_available_ssh_keys(self.available_ssh_keys)

        choices = [
            questionary.Choice(
                title=f"{key.name} ({key.id[:12]})", value=key.id  # type: ignore
            )
            for key in self.available_ssh_keys
        ]

        try:
            ssh_key_id = questionary.select("Select SSH key:", choices=choices).ask()
            if ssh_key_id is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.ssh_key_id = ssh_key_id
        except KeyboardInterrupt:
            raise

    def _select_or_filter_offer(self) -> None:
        """Allow user to filter offers or select from list."""
        try:
            # Ask for filters
            gpu_type = questionary.text(
                "GPU type (optional, press Enter to skip):", default=""
            ).ask()
            if gpu_type is None:
                raise KeyboardInterrupt("Import cancelled by user")
            gpu_type = gpu_type or None

            cloud_provider = questionary.text(
                "Cloud provider (optional, press Enter to skip):", default=""
            ).ask()
            if cloud_provider is None:
                raise KeyboardInterrupt("Import cancelled by user")
            cloud_provider = cloud_provider or None

            # Load offers with filters
            try:
                self.available_offers = self.offers_service.list_offers(
                    gpu_type=gpu_type, cloud_provider=cloud_provider
                )
            except ServiceError as e:
                self.display_manager.display_error(
                    ErrorDTO(
                        message=e.message,
                        error_type=e.error_type,
                        error_code=e.error_code,
                    )
                )
                self.available_offers = []

            if not self.available_offers:
                self.display_manager.display_error(
                    ErrorDTO(message="No offers found with the specified filters.")
                )
                return

            # Display offers and let user select
            self.display_manager.display_available_offers(self.available_offers)

            choices = [
                questionary.Choice(
                    title=f"{offer.instance_type} - {offer.cloud_provider} - ${offer.hourly_cost}/hr",
                    value=offer.id,
                )
                for offer in self.available_offers
            ]

            offer_id = questionary.select("Select offer:", choices=choices).ask()
            if offer_id is None:
                raise KeyboardInterrupt("Import cancelled by user")
            self.config.offer_id = offer_id
        except KeyboardInterrupt:
            raise

    def _display_summary(self) -> bool:
        """Show summary and confirm import."""
        self.display_manager.display_import_summary(self.config)  # type: ignore

        try:
            result = questionary.confirm(
                "Import node with these settings?", default=True
            ).ask()
            if result is None:
                raise KeyboardInterrupt("Import cancelled by user")
            return result
        except KeyboardInterrupt:
            raise

    def _import_node(self) -> None:
        """Execute the node import."""
        try:
            if self.config.import_type == "SSH":
                node_id = self.node_service.import_ssh_node(
                    hostname=self.config.hostname,
                    endpoint=self.config.endpoint,
                    username=self.config.username,
                    ssh_key_id=self.config.ssh_key_id,
                )
                self.config.imported_node_ids.append(node_id)
                self.display_manager.display_success(
                    f"SSH node {node_id} imported successfully!"
                )

            else:  # OFFER
                node_ids = self.node_service.import_from_offer(
                    hostname=self.config.hostname,
                    offer_id=self.config.offer_id,
                    amount=self.config.amount,
                )
                self.config.imported_node_ids.extend(node_ids)
                self.display_manager.display_success(
                    f"Cloud nodes {', '.join(node_ids)} imported successfully!"
                )

        except ServiceError as e:
            self.display_manager.display_error(
                ErrorDTO(
                    message=e.message,
                    error_type=e.error_type,
                    error_code=e.error_code,
                )
            )

    def _prompt_continue(self) -> bool:
        """Ask if user wants to import another node."""
        try:
            result = questionary.confirm("Import another node?", default=False).ask()
            if result is None:
                raise KeyboardInterrupt("Import cancelled by user")
            return result
        except KeyboardInterrupt:
            raise

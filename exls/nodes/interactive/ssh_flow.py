from __future__ import annotations

from typing import List, Optional

import questionary
from pydantic import StrictStr

from exls.core.base.display import UserCancellationException
from exls.core.commons.decorators import handle_interactive_flow_errors
from exls.core.commons.display import ipv4_address_validator, non_empty_string_validator
from exls.core.commons.service import generate_random_name
from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.nodes.display import ComposingNodeDisplayManager
from exls.nodes.dtos import NodesImportSSHRequestDTO
from exls.nodes.interactive.mappers import ssh_keys_to_questionary_choices


class NodeImportSshFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive SSH node import flow."""


class NodeImportSshFlow:
    """Flow for SSH node import configuration."""

    def __init__(
        self,
        available_ssh_keys: List[SshKeyDTO],
        display_manager: ComposingNodeDisplayManager,
    ):
        if not available_ssh_keys:
            raise ValueError(
                "No SSH keys available. Please add an SSH key first using 'exls management ssh-keys add'."
            )
        self._available_ssh_keys: List[SshKeyDTO] = available_ssh_keys
        self._display_manager: ComposingNodeDisplayManager = display_manager

    @handle_interactive_flow_errors(
        "node import", NodeImportSshFlowInterruptionException
    )
    def _run_single_node_import(self) -> NodesImportSSHRequestDTO:
        hostname: StrictStr = self._display_manager.ask_text(
            "Hostname:",
            default=generate_random_name(prefix="n"),
            validator=non_empty_string_validator,
        )

        endpoint: StrictStr = self._display_manager.ask_text(
            "Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
            validator=ipv4_address_validator,
        )

        username: StrictStr = self._display_manager.ask_text(
            "Username:",
            default="root",
            validator=non_empty_string_validator,
        )

        ssh_key_choices: List[questionary.Choice] = ssh_keys_to_questionary_choices(
            self._available_ssh_keys
        )
        ssh_key_choice: questionary.Choice = self._display_manager.ask_select_required(
            "Select SSH key:",
            choices=ssh_key_choices,
            default=ssh_key_choices[0],
        )
        ssh_key: Optional[SshKeyDTO] = next(
            (key for key in self._available_ssh_keys if key.id == str(ssh_key_choice)),
            None,
        )
        if not ssh_key:
            raise RuntimeError("Selected SSH key not found.")

        node_import_request: NodesImportSSHRequestDTO = NodesImportSSHRequestDTO(
            hostname=hostname,
            endpoint=endpoint,
            username=username,
            ssh_key_name=ssh_key.name,
            ssh_key_id=ssh_key.id,
        )

        return node_import_request

    @handle_interactive_flow_errors(
        "node import", NodeImportSshFlowInterruptionException
    )
    def _confirm_import(
        self, node_import_requests: List[NodesImportSSHRequestDTO]
    ) -> None:
        if not node_import_requests:
            return

        self._display_manager.display_info("Importing the following nodes:")
        self._display_manager.display_import_ssh_requests(node_import_requests)
        confirmed = self._display_manager.ask_confirm(
            "Import these nodes?", default=True
        )
        if not confirmed:
            raise NodeImportSshFlowInterruptionException(
                "Node import cancelled by user."
            )

    def run(self) -> List[NodesImportSSHRequestDTO]:
        """
        Collect SSH node import details and return DTO.

        Returns:
            A list of NodesImportSSHRequestDTO objects.
        """
        node_import_requests: List[NodesImportSSHRequestDTO] = []
        self._display_manager.display_info(
            "🚀 SSH Node Import - Interactive Mode: This will guide you through the process of importing nodes"
        )
        while True:
            try:
                node_import_requests.append(self._run_single_node_import())
                self._display_manager.display_info("Your current list of nodes:")
                self._display_manager.display_import_ssh_requests(node_import_requests)
            except NodeImportSshFlowInterruptionException:
                if not node_import_requests:
                    raise
                self._display_manager.display_info("Cancelled node import.")
                break

            add_another = self._display_manager.ask_confirm(
                "Do you want to import another node?", default=False
            )
            if not add_another:
                break

        self._confirm_import(node_import_requests)

        return node_import_requests

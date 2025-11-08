from __future__ import annotations

from typing import List

import questionary
from pydantic import StrictStr

from exls.core.base.display import UserCancellationException
from exls.core.base.exceptions import ExalsiusError
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

    def run(self) -> NodesImportSSHRequestDTO:
        """
        Collect SSH node import details and return DTO.

        Returns:
            NodesImportSSHRequestDTO if successful
        """
        try:
            self._display_manager.display_info(
                "🚀 SSH Node Import - Interactive Mode: This will guide you through importing a node"
            )

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
            ssh_key_id = self._display_manager.ask_select_required(
                "Select SSH key:",
                choices=ssh_key_choices,
                default=ssh_key_choices[0],
            )

            node_import_request: NodesImportSSHRequestDTO = NodesImportSSHRequestDTO(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_id=str(ssh_key_id),
            )

            self._display_manager.display_import_ssh_request(node_import_request)
            confirmed = self._display_manager.ask_confirm(
                "Import node with these settings?", default=True
            )
            if not confirmed:
                raise NodeImportSshFlowInterruptionException(
                    "SSH node import cancelled by user."
                )

        except UserCancellationException as e:
            raise NodeImportSshFlowInterruptionException(e) from e
        except Exception as e:
            raise ExalsiusError(f"An unexpected error occurred: {str(e)}") from e

        return node_import_request

from typing import TYPE_CHECKING, List, Optional

import questionary
from pydantic import StrictStr

from exls.core.commons.service import generate_random_name
from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.nodes.dtos import NodesImportSSHRequestDTO
from exls.nodes.interactive.base_flow import BaseNodeImportFlow
from exls.nodes.interactive.mappers import ssh_keys_to_questionary_choices

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class NodeImportSSHFlow(BaseNodeImportFlow):
    """Flow for SSH node import configuration."""

    def __init__(
        self,
        ssh_keys: List[SshKeyDTO],
        display_manager: "ComposingNodeDisplayManager",
    ):
        super().__init__(display_manager)
        if not ssh_keys:
            raise ValueError(
                "No SSH keys available. Please add an SSH key first using 'exls management ssh-keys add'."
            )
        self._ssh_keys: List[SshKeyDTO] = ssh_keys

    def run(self) -> Optional[NodesImportSSHRequestDTO]:
        """
        Collect SSH node import details and return DTO.

        Returns:
            NodesImportSSHRequestDTO if successful, None if cancelled
        """
        try:
            hostname: StrictStr = self._display_manager.ask_text(
                "Hostname:", default=generate_random_name(prefix="node")
            )

            endpoint: StrictStr = self._display_manager.ask_text(
                "Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
            )

            username: StrictStr = self._display_manager.ask_text(
                "Username:", default="root"
            )

            self._display_manager.display_ssh_keys(self._ssh_keys)

            ssh_key_choices: List[questionary.Choice] = ssh_keys_to_questionary_choices(
                self._ssh_keys
            )
            ssh_key_id = self._display_manager.ask_select_required(
                "Select SSH key:",
                choices=ssh_key_choices,
                default=ssh_key_choices[0],
            )

            dto = NodesImportSSHRequestDTO(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_id=str(ssh_key_id),
            )

            self._display_manager.display_import_ssh_request(dto)
            confirmed = self._display_manager.ask_confirm(
                "Import node with these settings?", default=True
            )

            if not confirmed:
                return None

            return dto

        except (KeyboardInterrupt, TypeError):
            return None

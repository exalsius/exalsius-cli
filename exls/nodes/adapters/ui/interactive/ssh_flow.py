from __future__ import annotations

from typing import List, Optional

import questionary

from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.nodes.adapters.cli.display import ComposingNodeDisplayManager
from exls.nodes.adapters.cli.mappers import ssh_keys_to_questionary_choices
from exls.nodes.adapters.dtos import ImportSelfmanagedNodeRequestDTO
from exls.shared.adapters.cli.decorators import handle_interactive_flow_errors
from exls.shared.adapters.cli.display import (
    ipv4_address_validator,
    non_empty_string_validator,
)
from exls.shared.adapters.cli.interactive import (
    FlowContext,
    SelectStep,
    SequentialFlow,
    TextInputStep,
)
from exls.shared.core.domain import generate_random_name
from exls.shared.core.ports import UserCancellationException


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
    def _run_single_node_import(self) -> ImportSelfmanagedNodeRequestDTO:
        context = FlowContext()

        ssh_key_choices: List[questionary.Choice] = ssh_keys_to_questionary_choices(
            self._available_ssh_keys
        )

        def get_random_hostname(_: FlowContext) -> str:
            return generate_random_name(prefix="n")

        flow = SequentialFlow(
            [
                TextInputStep(
                    key="hostname",
                    message="Hostname:",
                    default=get_random_hostname,
                    validator=non_empty_string_validator,
                ),
                TextInputStep(
                    key="endpoint",
                    message="Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
                    validator=ipv4_address_validator,
                ),
                TextInputStep(
                    key="username",
                    message="Username:",
                    default="ubuntu",
                    validator=non_empty_string_validator,
                ),
                SelectStep(
                    key="ssh_key_choice",
                    message="Select SSH key:",
                    choices=ssh_key_choices,
                    default=ssh_key_choices[0] if ssh_key_choices else None,
                ),
            ]
        )

        flow.execute(context, self._display_manager)

        hostname = str(context["hostname"])
        endpoint = str(context["endpoint"])
        username = str(context["username"])
        ssh_key_choice = context["ssh_key_choice"]

        ssh_key: Optional[SshKeyDTO] = next(
            (key for key in self._available_ssh_keys if key.id == str(ssh_key_choice)),
            None,
        )
        if not ssh_key:
            raise RuntimeError("Selected SSH key not found.")

        node_import_request: ImportSelfmanagedNodeRequestDTO = (
            ImportSelfmanagedNodeRequestDTO(
                hostname=hostname,
                endpoint=endpoint,
                username=username,
                ssh_key_name=ssh_key.name,
                ssh_key_id=ssh_key.id,
            )
        )

        return node_import_request

    @handle_interactive_flow_errors(
        "node import", NodeImportSshFlowInterruptionException
    )
    def _confirm_import(
        self, node_import_requests: List[ImportSelfmanagedNodeRequestDTO]
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

    def run(self) -> List[ImportSelfmanagedNodeRequestDTO]:
        """
        Collect SSH node import details and return DTO.

        Returns:
            A list of NodesImportSSHRequestDTO objects.
        """
        node_import_requests: List[ImportSelfmanagedNodeRequestDTO] = []
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

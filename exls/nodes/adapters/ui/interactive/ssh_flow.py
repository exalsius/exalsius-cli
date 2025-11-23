from __future__ import annotations

from typing import List, Optional

from exls.management.adapters.dtos import SshKeyDTO
from exls.nodes.adapters.dtos import ImportSelfmanagedNodeRequestDTO
from exls.nodes.adapters.ui.display.display import NodesInteractionManager
from exls.shared.adapters.decorators import handle_interactive_flow_errors
from exls.shared.adapters.ui.display.display import UserCancellationException
from exls.shared.adapters.ui.display.interfaces import IBaseInputManager
from exls.shared.adapters.ui.display.validators import (
    ipv4_address_validator,
    kubernetes_name_validator,
    non_empty_string_validator,
)
from exls.shared.adapters.ui.display.values import DisplayChoice, OutputFormat
from exls.shared.adapters.ui.interactive.flow import FlowContext, SequentialFlow
from exls.shared.adapters.ui.interactive.steps import SelectRequiredStep, TextInputStep
from exls.shared.core.domain import generate_random_name


class NodeImportSshFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive SSH node import flow."""


class NodeImportSshFlow:
    """Flow for SSH node import configuration."""

    def __init__(
        self,
        interaction_manager: NodesInteractionManager,
        available_ssh_keys: List[SshKeyDTO],
    ):
        self._interaction_manager: NodesInteractionManager = interaction_manager
        self._available_ssh_keys: List[SshKeyDTO] = available_ssh_keys

    @handle_interactive_flow_errors(
        "node import", NodeImportSshFlowInterruptionException
    )
    def _run_single_node_import(self) -> ImportSelfmanagedNodeRequestDTO:
        context = FlowContext()

        flow = SequentialFlow[IBaseInputManager](
            [
                TextInputStep(
                    key="hostname",
                    message="Hostname:",
                    default=generate_random_name(prefix="n"),
                    validator=kubernetes_name_validator,
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
                SelectRequiredStep(
                    key="ssh_key_choice",
                    message="Select SSH key:",
                    choices=[
                        DisplayChoice(title=key.name, value=key.id)
                        for key in self._available_ssh_keys
                    ],
                    default=(
                        DisplayChoice(
                            title=self._available_ssh_keys[0].name,
                            value=self._available_ssh_keys[0].id,
                        )
                        if self._available_ssh_keys
                        else None
                    ),
                ),
            ]
        )

        # We pass the input manager explicitly because the steps require IBaseInputManager
        flow.execute(context, self._interaction_manager.input_manager)

        hostname: str = str(context["hostname"])
        endpoint: str = str(context["endpoint"])
        username: str = str(context["username"])
        ssh_key_choice: str = str(context["ssh_key_choice"])

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

        self._interaction_manager.display_info_message(
            "Importing the following nodes:", OutputFormat.TEXT
        )
        self._interaction_manager.display_data(
            node_import_requests, output_format=OutputFormat.TABLE
        )
        confirmed = self._interaction_manager.input_manager.ask_confirm(
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
        self._interaction_manager.display_info_message(
            "🚀 SSH Node Import - Interactive Mode: This will guide you through the process of importing nodes",
            OutputFormat.TEXT,
        )
        while True:
            try:
                node_import_requests.append(self._run_single_node_import())
                self._interaction_manager.display_info_message(
                    "Your current list of nodes:", OutputFormat.TEXT
                )
                self._interaction_manager.display_data(
                    node_import_requests, output_format=OutputFormat.TABLE
                )
            except NodeImportSshFlowInterruptionException:
                if not node_import_requests:
                    raise
                self._interaction_manager.display_info_message(
                    "Cancelled node import.", OutputFormat.TEXT
                )
                break

            add_another = self._interaction_manager.input_manager.ask_confirm(
                "Do you want to import another node?", default=False
            )
            if not add_another:
                break

        self._confirm_import(node_import_requests)

        return node_import_requests

from __future__ import annotations

from typing import List

from pydantic import BaseModel

from exls.management.adapters.dtos import SshKeyDTO
from exls.nodes.adapters.dtos import ImportSelfmanagedNodeRequestDTO
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, SequentialFlow
from exls.shared.adapters.ui.flow.steps import SelectRequiredStep, TextInputStep
from exls.shared.adapters.ui.input.service import (
    ipv4_address_validator,
    kubernetes_name_validator,
    non_empty_string_validator,
)
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
    UserCancellationException,
)
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.domain import generate_random_name


class SelfmanagedNodeImportFlow:
    """Flow for self-managed node import configuration."""

    def __init__(
        self,
        io_facade: IIOFacade[BaseModel],
        available_ssh_keys: List[SshKeyDTO],
    ):
        self._io_facade: IIOFacade[BaseModel] = io_facade
        self._available_ssh_keys: List[SshKeyDTO] = available_ssh_keys

    def _run_single_node_import(self) -> ImportSelfmanagedNodeRequestDTO:
        context: FlowContext = FlowContext()

        flow = SequentialFlow(
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
                SelectRequiredStep[SshKeyDTO](
                    key="ssh_key_choice",
                    message="Select SSH key:",
                    choices=[
                        DisplayChoice[SshKeyDTO](title=key.name, value=key)
                        for key in self._available_ssh_keys
                    ],
                    default=(
                        DisplayChoice[SshKeyDTO](
                            title=self._available_ssh_keys[0].name,
                            value=self._available_ssh_keys[0],
                        )
                        if self._available_ssh_keys
                        else None
                    ),
                ),
            ]
        )

        # We pass the input manager explicitly because the steps require IBaseInputManager
        flow.execute(context, self._io_facade)

        hostname: str = context["hostname"]
        endpoint: str = context["endpoint"]
        username: str = context["username"]
        ssh_key: SshKeyDTO = context["ssh_key_choice"]

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

    def _confirm_import(
        self, node_import_requests: List[ImportSelfmanagedNodeRequestDTO]
    ) -> None:
        if not node_import_requests:
            return

        self._io_facade.display_info_message(
            message="Importing the following nodes:", output_format=OutputFormat.TEXT
        )
        self._io_facade.display_data(
            data=node_import_requests, output_format=OutputFormat.TABLE
        )
        confirmed = self._io_facade.ask_confirm(
            message="Import these nodes?", default=True
        )
        if not confirmed:
            raise UserCancellationException("Node import cancelled by user.")

    def run(self) -> List[ImportSelfmanagedNodeRequestDTO]:
        """
        Collect SSH node import details and return DTO.

        Returns:
            A list of NodesImportSSHRequestDTO objects.
        """
        node_import_requests: List[ImportSelfmanagedNodeRequestDTO] = []
        self._io_facade.display_info_message(
            message="🚀 SSH Node Import - Interactive Mode: This will guide you through the process of importing nodes",
            output_format=OutputFormat.TEXT,
        )
        while True:
            try:
                node_import_requests.append(self._run_single_node_import())
                self._io_facade.display_info_message(
                    message="Your current list of nodes:",
                    output_format=OutputFormat.TEXT,
                )
                self._io_facade.display_data(
                    data=node_import_requests, output_format=OutputFormat.TABLE
                )
            except UserCancellationException:
                if not node_import_requests:
                    raise
                self._io_facade.display_info_message(
                    message="Cancelled node import.", output_format=OutputFormat.TEXT
                )
                break

            add_another: bool = self._io_facade.ask_confirm(
                message="Do you want to import another node?", default=False
            )
            if not add_another:
                break

        self._confirm_import(node_import_requests)

        return node_import_requests

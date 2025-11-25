from __future__ import annotations

from typing import List

from pydantic import BaseModel

from exls.nodes.adapters.ui.dtos import (
    ImportSelfmanagedNodeRequestDTO,
    ImportSelfmanagedNodeRequestListDTO,
    NodesSshKeyDTO,
    NodesSshKeySpecificationDTO,
)
from exls.nodes.adapters.ui.flows.ports import IImportSshKeyFlow
from exls.nodes.core.service import NodesService
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowStep, SequentialFlow
from exls.shared.adapters.ui.flow.steps import (
    ConditionalStep,
    ListBuilderStep,
    SelectRequiredStep,
    SubModelStep,
    TextInputStep,
)
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

ADD_NEW_KEY_SENTINEL: object = object()


class ImportSelfmanagedNodeFlow(FlowStep[ImportSelfmanagedNodeRequestDTO]):
    """Flow for self-managed node import configuration."""

    def __init__(
        self,
        service: NodesService,
        import_ssh_key_flow: IImportSshKeyFlow,
    ):
        self._service: NodesService = service
        self._import_ssh_key_flow: IImportSshKeyFlow = import_ssh_key_flow

    def execute(
        self,
        model: ImportSelfmanagedNodeRequestDTO,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        """
        Collect SSH node import details and return DTO.

        Returns:
            A list of NodesImportSSHRequestDTO objects.
        """
        available_ssh_keys: List[NodesSshKeyDTO] = [
            NodesSshKeyDTO(id=key.id, name=key.name)
            for key in self._service.list_ssh_keys()
        ]

        choices: List[
            DisplayChoice[NodesSshKeyDTO | NodesSshKeySpecificationDTO | object]
        ] = [
            DisplayChoice[NodesSshKeyDTO | NodesSshKeySpecificationDTO | object](
                title=ssh_key.name, value=ssh_key
            )
            for ssh_key in available_ssh_keys
        ]
        choices.append(
            DisplayChoice[NodesSshKeyDTO | NodesSshKeySpecificationDTO | object](
                title="✨ Import a new SSH key...", value=ADD_NEW_KEY_SENTINEL
            )
        )

        flow: SequentialFlow[ImportSelfmanagedNodeRequestDTO] = SequentialFlow[
            ImportSelfmanagedNodeRequestDTO
        ](
            steps=[
                TextInputStep[ImportSelfmanagedNodeRequestDTO](
                    key="hostname",
                    message="Hostname:",
                    default=generate_random_name(prefix="n"),
                    validator=kubernetes_name_validator,
                ),
                TextInputStep[ImportSelfmanagedNodeRequestDTO](
                    key="endpoint",
                    message="Endpoint (IP address or hostname and port, e.g. 192.168.1.1:22):",
                    validator=ipv4_address_validator,
                ),
                TextInputStep[ImportSelfmanagedNodeRequestDTO](
                    key="username",
                    message="Username:",
                    default="ubuntu",
                    validator=non_empty_string_validator,
                ),
                SelectRequiredStep[
                    ImportSelfmanagedNodeRequestDTO,
                    NodesSshKeyDTO | NodesSshKeySpecificationDTO | object,
                ](
                    key="ssh_key",
                    message="Select SSH key:",
                    choices=choices,
                    default=choices[0],
                ),
                # Implement side-effect to update choices if new ssh key is imported; can be done via action step with callback to local method
                ConditionalStep[ImportSelfmanagedNodeRequestDTO](
                    condition=lambda model: model.ssh_key is ADD_NEW_KEY_SENTINEL,
                    true_step=SubModelStep[
                        ImportSelfmanagedNodeRequestDTO, NodesSshKeySpecificationDTO
                    ](
                        field_name="ssh_key",
                        child_step=self._import_ssh_key_flow,
                        child_model_class=NodesSshKeySpecificationDTO,
                    ),
                ),
            ]
        )

        flow.execute(model, io_facade)


class ImportSelfmanagedNodeRequestListFlow(
    FlowStep[ImportSelfmanagedNodeRequestListDTO]
):
    """Flow for self-managed node import list configuration."""

    def __init__(
        self,
        import_selfmanaged_node_flow: ImportSelfmanagedNodeFlow,
    ):
        self._import_selfmanaged_node_flow: ImportSelfmanagedNodeFlow = (
            import_selfmanaged_node_flow
        )

    def execute(
        self,
        model: ImportSelfmanagedNodeRequestListDTO,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        """
        Collect self-managed node import details and return DTO.
        """
        io_facade.display_info_message(
            message="🚀 Self-managed Node Import - Interactive Mode: This will guide you through the process of importing nodes",
            output_format=OutputFormat.TEXT,
        )

        flow: SequentialFlow[ImportSelfmanagedNodeRequestListDTO] = SequentialFlow[
            ImportSelfmanagedNodeRequestListDTO
        ](
            steps=[
                ListBuilderStep[
                    ImportSelfmanagedNodeRequestListDTO, ImportSelfmanagedNodeRequestDTO
                ](
                    key="nodes",
                    item_step=self._import_selfmanaged_node_flow,
                    item_model_class=ImportSelfmanagedNodeRequestDTO,
                    prompt_message="Do you want to add another node?",
                    min_items=1,
                ),
            ]
        )
        flow.execute(model, io_facade)

        io_facade.display_info_message(
            message="Importing the following nodes:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(
            data=model.nodes,
            output_format=OutputFormat.TABLE,
        )
        confirm: bool = io_facade.ask_confirm(
            message="Import these nodes?",
            default=True,
        )

        if not confirm:
            raise UserCancellationException("User cancelled the nodes import.")

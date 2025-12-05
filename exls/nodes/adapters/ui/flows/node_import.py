from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Union

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
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep, SequentialFlow
from exls.shared.adapters.ui.flow.steps import (
    ChoicesSpec,
    ConditionalStep,
    ListBuilderStep,
    SelectRequiredStep,
    SubModelStep,
    TextInputStep,
    UpdateLastChoiceStep,
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

_SSH_KEY_CHOICE = Union[NodesSshKeyDTO, NodesSshKeySpecificationDTO, object]


class ImportSelfmanagedNodeFlow(FlowStep[ImportSelfmanagedNodeRequestDTO]):
    """Flow for self-managed node import configuration."""

    def __init__(
        self,
        service: NodesService,
        import_ssh_key_flow: IImportSshKeyFlow,
        ask_confirmation: bool = True,
    ):
        self._service: NodesService = service
        self._import_ssh_key_flow: IImportSshKeyFlow = import_ssh_key_flow
        self._cached_ssh_keys: Optional[Sequence[NodesSshKeyDTO]] = None
        self._ask_confirmation: bool = ask_confirmation

    def _get_available_ssh_keys(self) -> Sequence[NodesSshKeyDTO]:
        if self._cached_ssh_keys is None:
            self._cached_ssh_keys = [
                NodesSshKeyDTO(id=key.id, name=key.name)
                for key in self._service.list_ssh_keys()
            ]
        return self._cached_ssh_keys

    def _get_ssh_key_choices(
        self, model: ImportSelfmanagedNodeRequestDTO, context: FlowContext
    ) -> ChoicesSpec[_SSH_KEY_CHOICE]:
        available_ssh_keys: Sequence[NodesSshKeyDTO] = self._get_available_ssh_keys()

        choices: List[DisplayChoice[_SSH_KEY_CHOICE]] = [
            DisplayChoice[_SSH_KEY_CHOICE](title=ssh_key.name, value=ssh_key)
            for ssh_key in available_ssh_keys
        ]
        added_choices: Dict[str, _SSH_KEY_CHOICE] = {c.title: c.value for c in choices}

        for sibling in context.siblings:
            if isinstance(sibling, ImportSelfmanagedNodeRequestDTO):
                if isinstance(sibling.ssh_key, NodesSshKeySpecificationDTO):
                    new_key_spec: NodesSshKeySpecificationDTO = sibling.ssh_key
                    if new_key_spec.name not in added_choices:
                        choices.append(
                            DisplayChoice[_SSH_KEY_CHOICE](
                                title=f"{new_key_spec.name} (New)",
                                value=new_key_spec,
                            )
                        )
                        added_choices[new_key_spec.name] = new_key_spec

        # 3. Add option to import new key
        choices.append(
            DisplayChoice[_SSH_KEY_CHOICE](
                title="✨ Import a new SSH key...", value=ADD_NEW_KEY_SENTINEL
            )
        )
        return ChoicesSpec[_SSH_KEY_CHOICE](choices=choices)

    def execute(
        self,
        model: ImportSelfmanagedNodeRequestDTO,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        """
        Collect SSH node import details and return DTO.

        Returns:
            A list of NodesImportSSHRequestDTO objects.
        """

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
                    message="Node's SSH username:",
                    default="",
                    validator=non_empty_string_validator,
                ),
                SelectRequiredStep[
                    ImportSelfmanagedNodeRequestDTO,
                    _SSH_KEY_CHOICE,
                ](
                    key="ssh_key",
                    message="Select SSH key:",
                    choices_spec=self._get_ssh_key_choices,
                ),
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
                UpdateLastChoiceStep[ImportSelfmanagedNodeRequestDTO](
                    key="ssh_key",
                ),
                # We could allow to cancel the subflow of ssh key import but we would need
                # to detect the cancellation and jump to a previous step.
            ]
        )

        flow.execute(model, context, io_facade)

        if self._ask_confirmation:
            try:
                io_facade.display_info_message(
                    message="Importing the following node:",
                    output_format=OutputFormat.TEXT,
                )
                io_facade.display_data(
                    data=model,
                    output_format=OutputFormat.TABLE,
                )
                confirm: bool = io_facade.ask_confirm(
                    message="Import this node?",
                    default=True,
                )
            except UserCancellationException:
                raise UserCancellationException("User cancelled the nodes import.")

            if not confirm:
                raise UserCancellationException("User cancelled the nodes import.")


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
        context: FlowContext,
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
        try:
            flow.execute(model, context, io_facade)
        except UserCancellationException:
            if not model.nodes:
                raise UserCancellationException("User cancelled the nodes import.")

        io_facade.display_info_message(
            message="Importing the following nodes:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(
            data=model.nodes,
            output_format=OutputFormat.TABLE,
        )
        try:
            confirm: bool = io_facade.ask_confirm(
                message="Import these nodes?",
                default=True,
            )
        except UserCancellationException:
            raise UserCancellationException("User cancelled the nodes import.")

        if not confirm:
            raise UserCancellationException("User cancelled the nodes import.")

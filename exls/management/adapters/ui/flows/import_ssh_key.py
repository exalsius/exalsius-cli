from __future__ import annotations

from pydantic import BaseModel

from exls.management.adapters.dtos import ImportSshKeyRequestDTO
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowStep, SequentialFlow
from exls.shared.adapters.ui.flow.steps import PathInputStep, TextInputStep
from exls.shared.adapters.ui.input.service import (
    non_empty_string_validator,
)
from exls.shared.adapters.ui.input.values import (
    UserCancellationException,
)
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.domain import generate_random_name


class ImportSshKeyFlow(FlowStep[ImportSshKeyRequestDTO]):
    """Flow for importing a new SSH key."""

    def _run(
        self, model: ImportSshKeyRequestDTO, io_facade: IIOFacade[BaseModel]
    ) -> None:
        flow = SequentialFlow[ImportSshKeyRequestDTO](
            [
                PathInputStep[ImportSshKeyRequestDTO](
                    key="key_path",
                    message="Path to SSH key file:",
                ),
                TextInputStep[ImportSshKeyRequestDTO](
                    key="name",
                    message="Name of the SSH key:",
                    default=generate_random_name(prefix="ssh-key"),
                    validator=non_empty_string_validator,
                ),
            ]
        )

        flow.execute(model, io_facade)

    def _confirm_import(
        self,
        add_ssh_key_request: ImportSshKeyRequestDTO,
        io_facade: IIOFacade[BaseModel],
    ) -> bool:
        io_facade.display_info_message(
            message="Importing the following SSH key:", output_format=OutputFormat.TEXT
        )
        io_facade.display_data(
            data=add_ssh_key_request, output_format=OutputFormat.TABLE
        )
        confirmed: bool = io_facade.ask_confirm(
            message="Import this SSH key?", default=True
        )
        return confirmed

    def execute(
        self, model: ImportSshKeyRequestDTO, io_facade: IIOFacade[BaseModel]
    ) -> None:
        """
        Collect SSH key import details and return DTO.

        Returns:
            A ImportSshKeyRequestDTO object.
        """
        io_facade.display_info_message(
            message="🚀 Importing a new SSH Key - Interactive Mode: This will guide you through the process of importing an SSH key",
            output_format=OutputFormat.TEXT,
        )

        self._run(model, io_facade)

        if not self._confirm_import(model, io_facade):
            raise UserCancellationException("SSH key import cancelled by user.")

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, StrictStr

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowCancelationByUserException,
    FlowContext,
    FlowStep,
    SequentialFlow,
)
from exls.shared.adapters.ui.flow.steps import PathInputStep, TextInputStep
from exls.shared.adapters.ui.input.service import (
    non_empty_string_validator,
)
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.utils import generate_random_name


class FlowImportSshKeyRequestDTO(BaseModel):
    name: StrictStr = Field(default="", description="The name of the SSH key")
    key_path: Path = Field(default=Path(""), description="The path to the SSH key file")


class ImportSshKeyFlow(FlowStep[FlowImportSshKeyRequestDTO]):
    """Flow for importing a new SSH key."""

    def __init__(self, ask_confirm: bool = True):
        self._ask_confirm: bool = ask_confirm

    def _run(
        self,
        model: FlowImportSshKeyRequestDTO,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        flow = SequentialFlow[FlowImportSshKeyRequestDTO](
            steps=[
                PathInputStep[FlowImportSshKeyRequestDTO](
                    key="key_path",
                    message="Path to SSH key file:",
                ),
                TextInputStep[FlowImportSshKeyRequestDTO](
                    key="name",
                    message="Name of the SSH key:",
                    default=generate_random_name(prefix="ssh-key"),
                    validator=non_empty_string_validator,
                ),
            ]
        )

        flow.execute(model, context, io_facade)

    def _confirm_import(
        self,
        add_ssh_key_request: FlowImportSshKeyRequestDTO,
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
        self,
        model: FlowImportSshKeyRequestDTO,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
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

        self._run(model, context, io_facade)

        if self._ask_confirm and not self._confirm_import(model, io_facade):
            raise FlowCancelationByUserException("SSH key import cancelled by user.")

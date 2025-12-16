from pydantic import BaseModel

from exls.management.adapters.dtos import ImportSshKeyRequestDTO
from exls.management.adapters.ui.flows.import_ssh_key import ImportSshKeyFlow
from exls.nodes.adapters.ui.flows.ports import (
    FlowNodesSshKeySpecification,
    IImportSshKeyFlow,
)
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext
from exls.shared.adapters.ui.output.values import OutputFormat


class ImportSshKeyManagementAdapterFlow(IImportSshKeyFlow):
    def __init__(self, import_ssh_key_flow: ImportSshKeyFlow):
        self._import_ssh_key_flow: ImportSshKeyFlow = import_ssh_key_flow

    def execute(
        self,
        model: FlowNodesSshKeySpecification,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        add_ssh_key_request: ImportSshKeyRequestDTO = ImportSshKeyRequestDTO()

        self._import_ssh_key_flow.execute(add_ssh_key_request, context, io_facade)

        model.name = add_ssh_key_request.name
        model.key_path = add_ssh_key_request.key_path

        io_facade.display_info_message(
            message="✅ Your new SSH key will be imported together with the nodes.",
            output_format=OutputFormat.TEXT,
        )

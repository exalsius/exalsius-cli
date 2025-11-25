from pydantic import BaseModel

from exls.management.adapters.dtos import ImportSshKeyRequestDTO
from exls.management.adapters.ui.flows.import_ssh_key import ImportSshKeyFlow
from exls.nodes.adapters.ui.dtos import NodesSshKeySpecificationDTO
from exls.nodes.adapters.ui.flows.ports import IImportSshKeyFlow
from exls.shared.adapters.ui.facade.interface import IIOFacade


class ImportSshKeyManagementAdapterFlow(IImportSshKeyFlow):
    def __init__(self, import_ssh_key_flow: ImportSshKeyFlow):
        self._import_ssh_key_flow: ImportSshKeyFlow = import_ssh_key_flow

    def execute(
        self, model: NodesSshKeySpecificationDTO, io_facade: IIOFacade[BaseModel]
    ) -> None:
        add_ssh_key_request: ImportSshKeyRequestDTO = ImportSshKeyRequestDTO()
        self._import_ssh_key_flow.execute(add_ssh_key_request, io_facade)

        model.name = add_ssh_key_request.name
        model.key_path = add_ssh_key_request.key_path

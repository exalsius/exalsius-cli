import typer

from exls.management.adapters.gateway.sdk import create_management_gateway
from exls.management.adapters.ui.display.display import IOManagementFacade
from exls.management.adapters.ui.flows.import_ssh_key import ImportSshKeyFlow
from exls.management.core.ports import IManagementGateway
from exls.management.core.service import ManagementService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.gateway.file.gateways import (
    IFileReadGateway,
    StringBase64FileReadGateway,
)
from exls.shared.adapters.ui.factory import IOFactory


class ManagementBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_management_service(self) -> ManagementService:
        management_gateway: IManagementGateway = create_management_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        fileio_gateway: IFileReadGateway[str] = StringBase64FileReadGateway()
        return ManagementService(
            management_gateway=management_gateway, fileio_gateway=fileio_gateway
        )

    def get_io_facade(self) -> IOManagementFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOManagementFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

    def get_import_ssh_key_flow(self, ask_confirm: bool = True) -> ImportSshKeyFlow:
        return ImportSshKeyFlow(ask_confirm=ask_confirm)

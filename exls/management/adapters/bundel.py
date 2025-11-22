import typer

from exls.management.adapters.gateway.sdk import create_management_gateway
from exls.management.adapters.ui.display.display import ManagementInteractionManager
from exls.management.core.ports import IManagementGateway
from exls.management.core.service import ManagementService
from exls.shared.adapters.bundle import SharedBundle
from exls.shared.adapters.gateway.file.gateways import (
    IFileReadGateway,
    StringBase64FileReadGateway,
)
from exls.shared.adapters.ui.display.factory import InteractionManagerFactory


class ManagementBundle(SharedBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_string_base64_file_reader(self) -> StringBase64FileReadGateway:
        return StringBase64FileReadGateway()

    def get_management_service(self) -> ManagementService:
        management_gateway: IManagementGateway = create_management_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        fileio_gateway: IFileReadGateway[str] = StringBase64FileReadGateway()
        return ManagementService(
            management_gateway=management_gateway, fileio_gateway=fileio_gateway
        )

    def get_interaction_manager(self) -> ManagementInteractionManager:
        interaction_manager_factory = InteractionManagerFactory()
        return ManagementInteractionManager(
            input_manager=interaction_manager_factory.get_input_manager(),
            output_manager=interaction_manager_factory.get_output_manager(),
        )

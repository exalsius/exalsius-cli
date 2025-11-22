import typer

from exls.services.adapters.gateway.sdk import create_services_gateway
from exls.services.adapters.ui.display.display import ServicesInteractionManager
from exls.services.core.ports import IServicesGateway
from exls.services.core.service import ServicesService
from exls.shared.adapters.bundle import SharedBundle
from exls.shared.adapters.ui.display.factory import InteractionManagerFactory


class ServicesBundle(SharedBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_services_service(self) -> ServicesService:
        services_gateway: IServicesGateway = create_services_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        return ServicesService(services_gateway=services_gateway)

    def get_interaction_manager(self) -> ServicesInteractionManager:
        interaction_manager_factory = InteractionManagerFactory()
        return ServicesInteractionManager(
            input_manager=interaction_manager_factory.get_input_manager(),
            output_manager=interaction_manager_factory.get_output_manager(),
        )

import typer

from exls.services.adapters.gateway.sdk import create_services_gateway
from exls.services.adapters.ui.display.display import IOServicesFacade
from exls.services.core.ports import IServicesGateway
from exls.services.core.service import ServicesService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory


class ServicesBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_services_service(self) -> ServicesService:
        services_gateway: IServicesGateway = create_services_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        return ServicesService(services_gateway=services_gateway)

    def get_io_facade(self) -> IOServicesFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOServicesFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

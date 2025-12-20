import typer
from exalsius_api_client.api.services_api import ServicesApi

from exls.services.adapters.gateway.gateway import ServicesGateway
from exls.services.adapters.gateway.sdk.sdk import ServicesGatewaySdk
from exls.services.core.service import ServicesService
from exls.shared.adapters.bundle import BaseBundle


class ServicesBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_services_service(self) -> ServicesService:
        services_api: ServicesApi = ServicesApi(api_client=self.create_api_client())
        services_gateway: ServicesGateway = ServicesGatewaySdk(
            services_api=services_api
        )
        return ServicesService(
            services_repository=services_gateway,
            services_operations=services_gateway,
        )

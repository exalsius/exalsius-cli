from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.services.domain import Service
from exls.services.dtos import (
    ServiceDTO,
    ServiceListRequestDTO,
)
from exls.services.gateway.base import ServicesGateway


class ServicesService:
    def __init__(self, services_gateway: ServicesGateway):
        self.services_gateway: ServicesGateway = services_gateway

    @handle_service_errors("listing services")
    def list_services(self, request: ServiceListRequestDTO) -> List[ServiceDTO]:
        services: List[Service] = self.services_gateway.list(request.cluster_id)
        return [ServiceDTO.from_domain(service) for service in services]

    @handle_service_errors("getting service")
    def get_service(self, service_id: str) -> ServiceDTO:
        service: Service = self.services_gateway.get(service_id=service_id)
        return ServiceDTO.from_domain(service)

    @handle_service_errors("deleting service")
    def delete_service(self, service_id: str) -> str:
        return self.services_gateway.delete(service_id=service_id)

    @handle_service_errors("creating service")
    def create_service(self) -> ServiceDTO:
        raise NotImplementedError("Creating services is not implemented")


def get_services_service(config: AppConfig, access_token: str) -> ServicesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    services_gateway: ServicesGateway = gateway_factory.create_services_gateway(
        access_token=access_token
    )
    return ServicesService(services_gateway=services_gateway)

from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.services.domain import Service, ServiceDeployParams, ServiceFilterParams
from exls.services.dtos import (
    CreateServiceRequestDTO,
    ServiceDTO,
    ServiceListRequestDTO,
)
from exls.services.gateway.base import ServicesGateway


class ServicesService:
    def __init__(self, services_gateway: ServicesGateway):
        self.services_gateway: ServicesGateway = services_gateway

    @handle_service_errors("listing services")
    def list_services(self, request: ServiceListRequestDTO) -> List[ServiceDTO]:
        service_filter_params: ServiceFilterParams = ServiceFilterParams(
            cluster_id=request.cluster_id
        )
        services: List[Service] = self.services_gateway.list(service_filter_params)
        return [ServiceDTO.from_domain(service) for service in services]

    @handle_service_errors("getting service")
    def get_service(self, service_id: str) -> ServiceDTO:
        service: Service = self.services_gateway.get(service_id)
        return ServiceDTO.from_domain(service)

    @handle_service_errors("deleting service")
    def delete_service(self, service_id: str) -> str:
        return self.services_gateway.delete(service_id)

    @handle_service_errors("creating service")
    def create_service(
        self,
        request: CreateServiceRequestDTO,
    ) -> ServiceDTO:
        deploy_params: ServiceDeployParams = ServiceDeployParams(
            cluster_id=request.cluster_id,
            name=request.name,
            service_template=request.service_template,
        )
        service_id: str = self.services_gateway.deploy(deploy_params)
        service: Service = self.services_gateway.get(service_id)
        return ServiceDTO.from_domain(service)


def get_services_service(config: AppConfig, access_token: str) -> ServicesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    services_gateway: ServicesGateway = gateway_factory.create_services_gateway()
    return ServicesService(services_gateway=services_gateway)

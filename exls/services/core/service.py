from typing import List

from exls.services.core.domain import Service
from exls.services.core.ports import IServicesGateway
from exls.shared.adapters.decorators import handle_service_layer_errors


class ServicesService:
    def __init__(self, services_gateway: IServicesGateway):
        self.services_gateway: IServicesGateway = services_gateway

    @handle_service_layer_errors("listing services")
    def list_services(self, cluster_id: str) -> List[Service]:
        return self.services_gateway.list(cluster_id)

    @handle_service_layer_errors("getting service")
    def get_service(self, service_id: str) -> Service:
        return self.services_gateway.get(service_id=service_id)

    @handle_service_layer_errors("deleting service")
    def delete_service(self, service_id: str) -> str:
        return self.services_gateway.delete(service_id=service_id)

    @handle_service_layer_errors("creating service")
    def deploy_service(self) -> Service:
        raise NotImplementedError("Creating services is not implemented")

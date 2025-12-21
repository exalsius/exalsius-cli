from typing import List

from exls.services.core.domain import Service
from exls.services.core.ports.operations import ServiceOperations
from exls.services.core.ports.repository import ServiceRepository
from exls.shared.core.decorators import handle_service_layer_errors

# TODO: Now domain service logic yet; like checking if cluster exists
#       or if service template exists etc.; need to be added.


class ServicesService:
    def __init__(
        self,
        services_repository: ServiceRepository,
        services_operations: ServiceOperations,
    ):
        self._services_repository: ServiceRepository = services_repository
        self._services_operations: ServiceOperations = services_operations

    @handle_service_layer_errors("listing services")
    def list_services(self, cluster_id: str) -> List[Service]:
        return self._services_repository.list(cluster_id)

    @handle_service_layer_errors("getting service")
    def get_service(self, service_id: str) -> Service:
        return self._services_repository.get(service_id=service_id)

    @handle_service_layer_errors("deleting service")
    def delete_service(self, service_id: str) -> str:
        return self._services_repository.delete(service_id=service_id)

    @handle_service_layer_errors("creating service")
    def deploy_service(self) -> Service:
        raise NotImplementedError("Creating services is not implemented")

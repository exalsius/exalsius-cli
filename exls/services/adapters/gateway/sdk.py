from typing import List

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exls.services.adapters.gateway.commands import (
    DeleteServiceSdkCommand,
    GetServiceSdkCommand,
    ListServicesSdkCommand,
)
from exls.services.adapters.gateway.mappers import service_from_sdk
from exls.services.core.domain import Service
from exls.services.core.ports import IServicesGateway
from exls.shared.adapters.gateway.sdk.service import create_api_client


class ServicesGatewaySdk(IServicesGateway):
    def __init__(self, services_api: ServicesApi):
        self._services_api = services_api

    def list(self, cluster_id: str) -> List[Service]:
        command: ListServicesSdkCommand = ListServicesSdkCommand(
            self._services_api, cluster_id=cluster_id
        )
        response: ServicesListResponse = command.execute()
        return [service_from_sdk(sdk_model=service) for service in response.services]

    def get(self, service_id: str) -> Service:
        command: GetServiceSdkCommand = GetServiceSdkCommand(
            self._services_api, service_id=service_id
        )
        response: ServiceResponse = command.execute()
        return service_from_sdk(sdk_model=response.service_deployment)

    def delete(self, service_id: str) -> str:
        command: DeleteServiceSdkCommand = DeleteServiceSdkCommand(
            self._services_api, service_id=service_id
        )
        response: ServiceDeleteResponse = command.execute()
        return response.service_deployment_id

    def deploy(self) -> str:
        raise NotImplementedError("Deploying services is not implemented")


def create_services_gateway(
    backend_host: str,
    access_token: str,
) -> ServicesGatewaySdk:
    services_api: ServicesApi = ServicesApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return ServicesGatewaySdk(services_api=services_api)

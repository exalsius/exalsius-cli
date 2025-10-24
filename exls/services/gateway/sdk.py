from typing import List

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service import Service as SdkService
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exls.services.domain import Service
from exls.services.gateway.base import ServicesGateway
from exls.services.gateway.commands import (
    DeleteServiceSdkCommand,
    GetServiceSdkCommand,
    ListServicesSdkCommand,
)


class ServicesGatewaySdk(ServicesGateway):
    def __init__(self, services_api: ServicesApi):
        self._services_api = services_api

    def _create_from_sdk_model(self, sdk_model: SdkService) -> Service:
        return Service(sdk_model=sdk_model)

    def list(self, cluster_id: str) -> List[Service]:
        command: ListServicesSdkCommand = ListServicesSdkCommand(
            self._services_api, params=cluster_id
        )
        response: ServicesListResponse = command.execute()
        return [
            self._create_from_sdk_model(sdk_model=sdk_service)
            for sdk_service in response.services
        ]

    def get(self, service_id: str) -> Service:
        command: GetServiceSdkCommand = GetServiceSdkCommand(
            self._services_api, service_id
        )
        response: ServiceResponse = command.execute()
        return self._create_from_sdk_model(sdk_model=response.service_deployment)

    def delete(self, service_id: str) -> str:
        command: DeleteServiceSdkCommand = DeleteServiceSdkCommand(
            self._services_api, service_id
        )
        response: ServiceDeleteResponse = command.execute()
        return response.service_deployment_id

    def deploy(self) -> str:
        raise NotImplementedError("Deploying services is not implemented")

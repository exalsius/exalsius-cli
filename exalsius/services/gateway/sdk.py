from typing import List

from exalsius_api_client.api.services_api import ServicesApi

from exalsius.services.domain import Service, ServiceDeployParams, ServiceFilterParams
from exalsius.services.gateway.base import ServicesGateway
from exalsius.services.gateway.commands import (
    DeleteServiceSdkCommand,
    DeployServiceSdkCommand,
    GetServiceSdkCommand,
    ListServicesSdkCommand,
)


class ServicesGatewaySdk(ServicesGateway):
    def __init__(self, services_api: ServicesApi):
        self._services_api = services_api

    def list(self, service_filter_params: ServiceFilterParams) -> List[Service]:
        command: ListServicesSdkCommand = ListServicesSdkCommand(
            self._services_api, service_filter_params
        )
        response: List[Service] = command.execute()
        return response

    def get(self, service_id: str) -> Service:
        command: GetServiceSdkCommand = GetServiceSdkCommand(
            self._services_api, service_id
        )
        response: Service = command.execute()
        return response

    def delete(self, service_id: str) -> str:
        command: DeleteServiceSdkCommand = DeleteServiceSdkCommand(
            self._services_api, service_id
        )
        response: str = command.execute()
        return response

    def deploy(self, deploy_params: ServiceDeployParams) -> str:
        command: DeployServiceSdkCommand = DeployServiceSdkCommand(
            self._services_api, deploy_params
        )
        response: str = command.execute()
        return response

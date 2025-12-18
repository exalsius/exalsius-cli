from typing import List

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service import Service as SdkService
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exls.services.adapters.gateway.gateway import ServicesGateway
from exls.services.adapters.gateway.sdk.commands import (
    DeleteServiceSdkCommand,
    GetServiceSdkCommand,
    ListServicesSdkCommand,
)
from exls.services.core.domain import Service


def _service_from_sdk(sdk_model: SdkService) -> Service:
    return Service(
        id=sdk_model.id or "",
        name=sdk_model.name,
        cluster_id=sdk_model.cluster_id,
        service_template=sdk_model.template.name,
        created_at=sdk_model.created_at,
    )


class ServicesGatewaySdk(ServicesGateway):
    def __init__(self, services_api: ServicesApi):
        self._services_api = services_api

    def list(self, cluster_id: str) -> List[Service]:
        command: ListServicesSdkCommand = ListServicesSdkCommand(
            self._services_api, cluster_id=cluster_id
        )
        response: ServicesListResponse = command.execute()
        return [_service_from_sdk(sdk_model=service) for service in response.services]

    def get(self, service_id: str) -> Service:
        command: GetServiceSdkCommand = GetServiceSdkCommand(
            self._services_api, service_id=service_id
        )
        response: ServiceResponse = command.execute()
        return _service_from_sdk(sdk_model=response.service_deployment)

    def delete(self, service_id: str) -> str:
        command: DeleteServiceSdkCommand = DeleteServiceSdkCommand(
            self._services_api, service_id=service_id
        )
        response: ServiceDeleteResponse = command.execute()
        return response.service_deployment_id

    def deploy(self) -> str:
        raise NotImplementedError("Deploying services is not implemented")

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_deployment_create_request import (
    ServiceDeploymentCreateRequest,
)
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exls.shared.adapters.sdk.command import ExalsiusSdkCommand


class BaseServicesSdkCommand[T_Cmd_Return](
    ExalsiusSdkCommand[ServicesApi, T_Cmd_Return]
):
    """Base class for all services commands."""

    pass


class ListServicesSdkCommand(BaseServicesSdkCommand[ServicesListResponse]):
    def __init__(self, api_client: ServicesApi, cluster_id: str):
        super().__init__(api_client)
        self._cluster_id: str = cluster_id

    def _execute_api_call(self) -> ServicesListResponse:
        response: ServicesListResponse = self.api_client.list_services_deployments(
            cluster_id=self._cluster_id
        )
        return response


class GetServiceSdkCommand(BaseServicesSdkCommand[ServiceResponse]):
    def __init__(self, api_client: ServicesApi, service_id: str):
        super().__init__(api_client)
        self._service_id: str = service_id

    def _execute_api_call(self) -> ServiceResponse:
        response: ServiceResponse = self.api_client.describe_service_deployment(
            service_deployment_id=self._service_id
        )
        return response


class DeleteServiceSdkCommand(BaseServicesSdkCommand[ServiceDeleteResponse]):
    def __init__(self, api_client: ServicesApi, service_id: str):
        super().__init__(api_client)
        self._service_id: str = service_id

    def _execute_api_call(self) -> ServiceDeleteResponse:
        response: ServiceDeleteResponse = self.api_client.delete_service_deployment(
            service_deployment_id=self._service_id
        )
        return response


class DeployServiceSdkCommand(BaseServicesSdkCommand[ServiceCreateResponse]):
    def __init__(
        self, api_client: ServicesApi, request: ServiceDeploymentCreateRequest
    ):
        super().__init__(api_client)
        self._request: ServiceDeploymentCreateRequest = request

    def _execute_api_call(self) -> ServiceCreateResponse:
        response: ServiceCreateResponse = self.api_client.create_service_deployment(
            service_deployment_create_request=self._request
        )
        return response

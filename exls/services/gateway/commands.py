from typing import Optional

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_deployment_create_request import (
    ServiceDeploymentCreateRequest,
)
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exls.core.commons.gateways.commands.sdk import ExalsiusSdkCommand


class BaseServicesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[ServicesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all services commands."""

    pass


class ListServicesSdkCommand(BaseServicesSdkCommand[str, ServicesListResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ServicesListResponse:
        assert params is not None
        response: ServicesListResponse = self.api_client.list_services_deployments(
            cluster_id=params
        )
        return response


class GetServiceSdkCommand(BaseServicesSdkCommand[str, ServiceResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ServiceResponse:
        assert params is not None
        response: ServiceResponse = self.api_client.describe_service_deployment(
            service_deployment_id=params
        )
        return response


class DeleteServiceSdkCommand(BaseServicesSdkCommand[str, ServiceDeleteResponse]):
    def _execute_api_call(self, params: Optional[str]) -> ServiceDeleteResponse:
        assert params is not None
        response: ServiceDeleteResponse = self.api_client.delete_service_deployment(
            service_deployment_id=params
        )
        return response


class DeployServiceSdkCommand(
    BaseServicesSdkCommand[ServiceDeploymentCreateRequest, ServiceCreateResponse]
):
    def _execute_api_call(
        self, params: Optional[ServiceDeploymentCreateRequest]
    ) -> ServiceCreateResponse:
        assert params is not None
        response: ServiceCreateResponse = self.api_client.create_service_deployment(
            service_deployment_create_request=params
        )
        return response

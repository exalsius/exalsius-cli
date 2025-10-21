from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service import Service as SdkService
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_deployment_create_request import (
    ServiceDeploymentCreateRequest,
)
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exalsius.core.commons.commands.sdk import ExalsiusSdkCommand
from exalsius.services.domain import Service, ServiceDeployParams, ServiceFilterParams


def _create_from_sdk_model(sdk_model: SdkService) -> Service:
    return Service(sdk_model=sdk_model)


class BaseServicesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[ServicesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all services commands."""

    pass


class ListServicesSdkCommand(
    BaseServicesSdkCommand[ServiceFilterParams, list[Service]]
):
    def _execute_api_call(self, params: ServiceFilterParams | None) -> list[Service]:
        assert params is not None
        response: ServicesListResponse = self.api_client.list_services_deployments(
            cluster_id=params.cluster_id
        )
        return [_create_from_sdk_model(service) for service in response.services]


class GetServiceSdkCommand(BaseServicesSdkCommand[str, Service]):
    def _execute_api_call(self, params: str | None) -> Service:
        assert params is not None
        response: ServiceResponse = self.api_client.describe_service_deployment(
            service_deployment_id=params
        )
        return _create_from_sdk_model(response.service_deployment)


class DeleteServiceSdkCommand(BaseServicesSdkCommand[str, str]):
    def _execute_api_call(self, params: str | None) -> str:
        assert params is not None
        response: ServiceDeleteResponse = self.api_client.delete_service_deployment(
            service_deployment_id=params
        )
        return response.service_deployment_id


class DeployServiceSdkCommand(BaseServicesSdkCommand[ServiceDeployParams, str]):
    def _execute_api_call(self, params: ServiceDeployParams | None) -> str:
        # we need the nullable params in the signature to be LSP compliant; therefore assert
        assert params is not None
        service_template = params.service_template.to_api_model()
        response: ServiceCreateResponse = self.api_client.create_service_deployment(
            service_deployment_create_request=ServiceDeploymentCreateRequest(
                cluster_id=params.cluster_id,
                name=params.name,
                template=service_template,
            )
        )
        return response.service_deployment_id

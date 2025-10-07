from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.services.models import (
    ServicesDeleteRequestDTO,
    ServicesDeployRequestDTO,
    ServicesGetRequestDTO,
    ServicesListRequestDTO,
)


class ListServicesCommand(
    ExalsiusAPICommand[ServicesApi, ServicesListRequestDTO, ServicesListResponse]
):
    def _execute_api_call(self) -> ServicesListResponse:
        return self.api_client.list_services_deployments(self.request.cluster_id)


class GetServiceCommand(
    ExalsiusAPICommand[ServicesApi, ServicesGetRequestDTO, ServiceResponse]
):
    def _execute_api_call(self) -> ServiceResponse:
        return self.api_client.describe_service_deployment(
            service_deployment_id=self.request.service_id
        )


class DeleteServiceCommand(
    ExalsiusAPICommand[ServicesApi, ServicesDeleteRequestDTO, ServiceDeleteResponse]
):
    def _execute_api_call(self) -> ServiceDeleteResponse:
        return self.api_client.delete_service_deployment(
            service_deployment_id=self.request.service_id
        )


class DeployServiceCommand(
    ExalsiusAPICommand[ServicesApi, ServicesDeployRequestDTO, ServiceCreateResponse]
):
    def _execute_api_call(self) -> ServiceCreateResponse:
        return self.api_client.create_service_deployment(
            service_deployment_create_request=self.request.get_api_model()
        )

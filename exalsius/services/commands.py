from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_deployment_create_request import (
    ServiceDeploymentCreateRequest,
)
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.service_template import ServiceTemplate
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.services.models import (
    ServicesDeleteRequestDTO,
    ServicesDeployRequestDTO,
    ServicesGetRequestDTO,
    ServicesListRequestDTO,
)


class ListServicesCommand(BaseCommand[ServicesListResponse]):
    def __init__(self, request: ServicesListRequestDTO):
        self.request: ServicesListRequestDTO = request

    def execute(self) -> ServicesListResponse:
        return self.request.api.list_services_deployments(self.request.cluster_id)


class GetServiceCommand(BaseCommand[ServiceResponse]):
    def __init__(self, request: ServicesGetRequestDTO):
        self.request: ServicesGetRequestDTO = request

    def execute(self) -> ServiceResponse:
        return self.request.api.describe_service_deployment(
            service_deployment_id=self.request.service_id
        )


class DeleteServiceCommand(BaseCommand[ServiceDeleteResponse]):
    def __init__(self, request: ServicesDeleteRequestDTO):
        self.request: ServicesDeleteRequestDTO = request

    def execute(self) -> ServiceDeleteResponse:
        return self.request.api.delete_service_deployment(
            service_deployment_id=self.request.service_id
        )


class DeployServiceCommand(BaseCommand[ServiceCreateResponse]):
    def __init__(self, request: ServicesDeployRequestDTO):
        self.request: ServicesDeployRequestDTO = request

    def execute(self) -> ServiceCreateResponse:
        service_template: ServiceTemplate = (
            self.request.service_template_factory.create_service_template()
        )

        service_deployment_create_request = ServiceDeploymentCreateRequest(
            cluster_id=self.request.cluster_id,
            name=service_template.name,
            template=service_template,
        )

        return self.request.api.create_service_deployment(
            service_deployment_create_request=service_deployment_create_request
        )

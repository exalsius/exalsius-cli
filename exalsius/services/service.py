from typing import Any, List

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.service import Service
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.services.commands import (
    DeleteServiceCommand,
    DeployServiceCommand,
    GetServiceCommand,
    ListServicesCommand,
)
from exalsius.services.models import (
    BaseServiceTemplateDTO,
    ServicesDeleteRequestDTO,
    ServicesDeployRequestDTO,
    ServicesGetRequestDTO,
    ServicesListRequestDTO,
)

SERVICES_API_ERROR_TYPE: str = "ServicesApiError"


class ServicesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.services_api: ServicesApi = ServicesApi(self.api_client)

    def _execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=SERVICES_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=SERVICES_API_ERROR_TYPE,
            )

    def list_services(self, cluster_id: str) -> List[Service]:
        command: ListServicesCommand = ListServicesCommand(
            ServicesListRequestDTO(
                api=self.services_api,
                cluster_id=cluster_id,
            )
        )
        response: ServicesListResponse = self._execute_command(command)
        return response.services

    def get_service(self, service_id: str) -> Service:
        command: GetServiceCommand = GetServiceCommand(
            ServicesGetRequestDTO(
                api=self.services_api,
                service_id=service_id,
            )
        )
        response: ServiceResponse = self._execute_command(command)
        return response.service_deployment

    def delete_service(self, service_id: str) -> str:
        command: DeleteServiceCommand = DeleteServiceCommand(
            ServicesDeleteRequestDTO(
                api=self.services_api,
                service_id=service_id,
            )
        )
        response: ServiceDeleteResponse = self._execute_command(command)
        return response.service_deployment_id

    def deploy_service(
        self,
        cluster_id: str,
        name: str,
        service_template: BaseServiceTemplateDTO,
    ) -> str:
        request: ServicesDeployRequestDTO = ServicesDeployRequestDTO(
            api=self.services_api,
            cluster_id=cluster_id,
            name=name,
            service_template=service_template,
        )
        command: DeployServiceCommand = DeployServiceCommand(request)
        response: ServiceCreateResponse = self._execute_command(command)
        return response.service_deployment_id

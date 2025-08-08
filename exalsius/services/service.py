from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.services_list_response import ServicesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth, T
from exalsius.core.commons.models import ServiceError
from exalsius.services.commands import (
    DeleteServiceCommand,
    DeployServiceCommand,
    GetServiceCommand,
    ListServicesCommand,
)
from exalsius.services.models import (
    ServicesDeleteRequestDTO,
    ServicesDeployRequestDTO,
    ServicesGetRequestDTO,
    ServicesListRequestDTO,
    ServiceTemplates,
)


class ServicesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.services_api: ServicesApi = ServicesApi(self.api_client)

    def _execute_command(self, command: BaseCommand[T]) -> T:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                f"api error while executing command {command.__class__.__name__}. "
                f"Error code: {e.status}, error body: {e.body}"
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {e}"
            )

    def list_services(self, cluster_id: str) -> ServicesListResponse:
        return self.execute_command(
            ListServicesCommand(
                ServicesListRequestDTO(
                    api=self.services_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def get_service(self, service_id: str) -> ServiceResponse:
        return self.execute_command(
            GetServiceCommand(
                ServicesGetRequestDTO(
                    api=self.services_api,
                    service_id=service_id,
                )
            )
        )

    def delete_service(self, service_id: str) -> ServiceDeleteResponse:
        return self.execute_command(
            DeleteServiceCommand(
                ServicesDeleteRequestDTO(
                    api=self.services_api,
                    service_id=service_id,
                )
            )
        )

    def deploy_service(
        self,
        cluster_id: str,
        name: str,
        service_template: ServiceTemplates,
    ) -> ServiceCreateResponse:
        return self.execute_command(
            DeployServiceCommand(
                request=ServicesDeployRequestDTO(
                    api=self.services_api,
                    cluster_id=cluster_id,
                    name=name,
                    service_template=service_template,
                )
            )
        )

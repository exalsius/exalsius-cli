from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.service_template import ServiceTemplate
from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.management.service_templates.commands import ListServiceTemplatesCommand
from exalsius.management.service_templates.models import ListServiceTemplatesRequestDTO

SERVICE_TEMPLATES_API_ERROR_TYPE: str = "ServiceTemplatesApiError"


class ServiceTemplatesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def list_service_templates(self) -> List[ServiceTemplate]:
        req: ListServiceTemplatesRequestDTO = ListServiceTemplatesRequestDTO(
            api=ManagementApi(self.api_client)
        )
        command: ListServiceTemplatesCommand = ListServiceTemplatesCommand(request=req)
        try:
            response: ServiceTemplateListResponse = self.execute_command(command)
            return response.service_templates
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
                error_type=SERVICE_TEMPLATES_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=SERVICE_TEMPLATES_API_ERROR_TYPE,
            )

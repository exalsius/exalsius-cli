from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.management.service_templates.models import ListServiceTemplatesRequestDTO


class ListServiceTemplatesCommand(
    ExalsiusAPICommand[
        ManagementApi, ListServiceTemplatesRequestDTO, ServiceTemplateListResponse
    ]
):
    def _execute_api_call(self) -> ServiceTemplateListResponse:
        return self.api_client.list_service_templates()

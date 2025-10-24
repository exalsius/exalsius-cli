from typing import Optional

from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand


class ListServiceTemplatesSdkCommand(
    BaseManagementSdkCommand[None, ServiceTemplateListResponse]
):
    def _execute_api_call(self, params: Optional[None]) -> ServiceTemplateListResponse:
        response: ServiceTemplateListResponse = self.api_client.list_service_templates()
        return response

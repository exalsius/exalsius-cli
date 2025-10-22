from typing import List, Optional

from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand
from exls.management.types.service_templates.domain import (
    ServiceTemplate,
    ServiceTemplateFilterParams,
)


class ListServiceTemplatesSdkCommand(
    BaseManagementSdkCommand[ServiceTemplateFilterParams, List[ServiceTemplate]]
):
    def _execute_api_call(
        self, params: Optional[ServiceTemplateFilterParams]
    ) -> List[ServiceTemplate]:
        response: ServiceTemplateListResponse = self.api_client.list_service_templates()
        return [
            ServiceTemplate(sdk_model=service_template)
            for service_template in response.service_templates
        ]

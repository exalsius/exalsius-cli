from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.service_template import (
    ServiceTemplate as SdkServiceTemplate,
)
from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exls.management.types.service_templates.domain import (
    ServiceTemplate,
)
from exls.management.types.service_templates.gateway.base import (
    ServiceTemplatesGateway,
)
from exls.management.types.service_templates.gateway.commands import (
    ListServiceTemplatesSdkCommand,
)


class ServiceTemplatesGatewaySdk(ServiceTemplatesGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def _create_service_template_from_sdk_model(
        self, sdk_model: SdkServiceTemplate
    ) -> ServiceTemplate:
        return ServiceTemplate(sdk_model=sdk_model)

    def list(self) -> List[ServiceTemplate]:
        command = ListServiceTemplatesSdkCommand(self._management_api, params=None)
        response: ServiceTemplateListResponse = command.execute()
        return [
            self._create_service_template_from_sdk_model(sdk_model=st)
            for st in response.service_templates
        ]

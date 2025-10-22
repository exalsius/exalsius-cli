from typing import List

from exalsius_api_client.api.management_api import ManagementApi

from exls.management.types.service_templates.domain import (
    ServiceTemplate,
    ServiceTemplateFilterParams,
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

    def list(self, params: ServiceTemplateFilterParams) -> List[ServiceTemplate]:
        command = ListServiceTemplatesSdkCommand(self._management_api, params)
        response: List[ServiceTemplate] = command.execute()
        return response

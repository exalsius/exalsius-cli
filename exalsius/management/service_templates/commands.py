from typing import List

from exalsius_api_client.models.service_template import ServiceTemplate
from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)

from exalsius.core.base.commands import BaseCommand
from exalsius.management.service_templates.models import ListServiceTemplatesRequestDTO


class ListServiceTemplatesCommand(BaseCommand):
    def __init__(self, request: ListServiceTemplatesRequestDTO):
        self.request: ListServiceTemplatesRequestDTO = request

    def execute(self) -> List[ServiceTemplate]:
        response: ServiceTemplateListResponse = (
            self.request.api.list_service_templates()
        )
        return response.service_templates

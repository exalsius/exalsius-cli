from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.management.types.service_templates.domain import (
    ServiceTemplate,
    ServiceTemplateFilterParams,
)
from exls.management.types.service_templates.dtos import (
    ListServiceTemplatesRequestDTO,
    ServiceTemplateDTO,
)
from exls.management.types.service_templates.gateway.base import (
    ServiceTemplatesGateway,
)


class ServiceTemplatesService:
    def __init__(self, service_templates_gateway: ServiceTemplatesGateway):
        self.service_templates_gateway = service_templates_gateway

    @handle_service_errors("listing service templates")
    def list_service_templates(
        self, request: ListServiceTemplatesRequestDTO
    ) -> List[ServiceTemplateDTO]:
        service_templates: List[ServiceTemplate] = self.service_templates_gateway.list(
            ServiceTemplateFilterParams()
        )
        return [ServiceTemplateDTO.from_domain(st) for st in service_templates]


def get_service_templates_service(
    config: AppConfig, access_token: str
) -> ServiceTemplatesService:
    gateway_factory = GatewayFactory(config=config, access_token=access_token)
    service_templates_gateway: ServiceTemplatesGateway = (
        gateway_factory.create_service_templates_gateway()
    )
    return ServiceTemplatesService(
        service_templates_gateway=service_templates_gateway,
    )

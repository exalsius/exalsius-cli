from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.management.types.cluster_templates.domain import (
    ClusterTemplate,
    ClusterTemplateFilterParams,
)
from exls.management.types.cluster_templates.dtos import (
    ClusterTemplateDTO,
    ListClusterTemplatesRequestDTO,
)
from exls.management.types.cluster_templates.gateway.base import (
    ClusterTemplatesGateway,
)


class ClusterTemplateService:
    def __init__(
        self,
        cluster_templates_gateway: ClusterTemplatesGateway,
    ):
        self.cluster_templates_gateway: ClusterTemplatesGateway = (
            cluster_templates_gateway
        )

    @handle_service_errors("listing cluster templates")
    def list_cluster_templates(
        self, request: ListClusterTemplatesRequestDTO
    ) -> List[ClusterTemplateDTO]:
        cluster_template_filter_params: ClusterTemplateFilterParams = (
            ClusterTemplateFilterParams()
        )
        cluster_templates: List[ClusterTemplate] = self.cluster_templates_gateway.list(
            cluster_template_filter_params
        )
        return [ClusterTemplateDTO.from_domain(c) for c in cluster_templates]


def get_cluster_templates_service(
    config: AppConfig, access_token: str
) -> ClusterTemplateService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    cluster_templates_gateway: ClusterTemplatesGateway = (
        gateway_factory.create_cluster_templates_gateway()
    )
    return ClusterTemplateService(
        cluster_templates_gateway=cluster_templates_gateway,
    )

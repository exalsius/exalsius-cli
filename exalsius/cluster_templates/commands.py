from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.cluster_templates.models import ListClusterTemplatesRequestDTO
from exalsius.core.base.commands import BaseCommand


class ListClusterTemplatesCommand(BaseCommand[ClusterTemplateListResponse]):
    def __init__(self, request: ListClusterTemplatesRequestDTO):
        self.request: ListClusterTemplatesRequestDTO = request

    def execute(self) -> ClusterTemplateListResponse:
        return self.request.api.list_cluster_templates()

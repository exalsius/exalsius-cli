from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.core.base.commands import BaseCommand
from exalsius.management.cluster_templates.models import ListClusterTemplatesRequestDTO


class ListClusterTemplatesCommand(BaseCommand):
    def __init__(self, request: ListClusterTemplatesRequestDTO):
        self.request: ListClusterTemplatesRequestDTO = request

    def execute(self) -> ClusterTemplateListResponse:
        return self.request.api.list_cluster_templates()

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.management.cluster_templates.models import ListClusterTemplatesRequestDTO


class ListClusterTemplatesCommand(
    ExalsiusAPICommand[
        ManagementApi, ListClusterTemplatesRequestDTO, ClusterTemplateListResponse
    ]
):
    def _execute_api_call(self) -> ClusterTemplateListResponse:
        return self.api_client.list_cluster_templates()

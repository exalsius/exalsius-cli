from typing import Optional

from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand


class ListClusterTemplatesSdkCommand(
    BaseManagementSdkCommand[None, ClusterTemplateListResponse]
):
    def _execute_api_call(self, params: Optional[None]) -> ClusterTemplateListResponse:
        response: ClusterTemplateListResponse = self.api_client.list_cluster_templates()
        return response

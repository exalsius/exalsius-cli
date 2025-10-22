from typing import List

from exalsius_api_client.api.management_api import ManagementApi

from exls.management.types.cluster_templates.domain import (
    ClusterTemplate,
    ClusterTemplateFilterParams,
)
from exls.management.types.cluster_templates.gateway.base import (
    ClusterTemplatesGateway,
)
from exls.management.types.cluster_templates.gateway.commands import (
    ListClusterTemplatesSdkCommand,
)


class ClusterTemplatesGatewaySdk(ClusterTemplatesGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list(self, params: ClusterTemplateFilterParams) -> List[ClusterTemplate]:
        command = ListClusterTemplatesSdkCommand(self._management_api, params)
        response: List[ClusterTemplate] = command.execute()
        return response

from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.cluster_template import (
    ClusterTemplate as SdkClusterTemplate,
)
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exls.management.types.cluster_templates.domain import ClusterTemplate
from exls.management.types.cluster_templates.gateway.base import (
    ClusterTemplatesGateway,
)
from exls.management.types.cluster_templates.gateway.commands import (
    ListClusterTemplatesSdkCommand,
)


class ClusterTemplatesGatewaySdk(ClusterTemplatesGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def _create_cluster_template_from_sdk_model(
        self,
        sdk_model: SdkClusterTemplate,
    ) -> ClusterTemplate:
        return ClusterTemplate(sdk_model=sdk_model)

    def list(self) -> List[ClusterTemplate]:
        command = ListClusterTemplatesSdkCommand(self._management_api, params=None)
        response: ClusterTemplateListResponse = command.execute()
        return [
            self._create_cluster_template_from_sdk_model(sdk_model=ct)
            for ct in response.cluster_templates
        ]

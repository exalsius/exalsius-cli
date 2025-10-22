from typing import List, Optional

from exalsius_api_client.models.cluster_template import (
    ClusterTemplate as SdkClusterTemplate,
)
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exls.management.commons.commands import BaseManagementSdkCommand
from exls.management.types.cluster_templates.domain import (
    ClusterTemplate,
    ClusterTemplateFilterParams,
)


def _create_cluster_template_from_sdk_model(
    sdk_model: SdkClusterTemplate,
) -> ClusterTemplate:
    return ClusterTemplate(sdk_model=sdk_model)


class ListClusterTemplatesSdkCommand(
    BaseManagementSdkCommand[ClusterTemplateFilterParams, List[ClusterTemplate]]
):
    def _execute_api_call(
        self, params: Optional[ClusterTemplateFilterParams]
    ) -> List[ClusterTemplate]:
        response: ClusterTemplateListResponse = self.api_client.list_cluster_templates()
        return [
            _create_cluster_template_from_sdk_model(ct)
            for ct in response.cluster_templates
        ]

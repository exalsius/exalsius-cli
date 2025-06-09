from typing import List, Optional, Tuple

import exalsius_api_client
from exalsius_api_client import ManagementApi
from exalsius_api_client.models.cluster_template import ClusterTemplate
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.core.operations.base import ListOperation


class ListClusterTemplatesOperation(ListOperation[ClusterTemplate]):
    def __init__(self, api_client: exalsius_api_client.ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[List[ClusterTemplate], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            cluster_templates_list_response: ClusterTemplateListResponse = (
                api_instance.list_cluster_templates()
            )
        except Exception as e:
            return None, str(e)
        return cluster_templates_list_response.cluster_templates, None

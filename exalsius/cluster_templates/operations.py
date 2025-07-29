from typing import Optional, Tuple

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.base.operations import BaseOperation


class ListClusterTemplatesOperation(BaseOperation[ClusterTemplateListResponse]):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[Optional[ClusterTemplateListResponse], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            cluster_templates_list_response: ClusterTemplateListResponse = (
                api_instance.list_cluster_templates()
            )
            return cluster_templates_list_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"

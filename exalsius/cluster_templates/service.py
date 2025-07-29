from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)

from exalsius.cluster_templates.commands import ListClusterTemplatesCommand
from exalsius.cluster_templates.models import ListClusterTemplatesRequestDTO
from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError


class ClusterTemplateService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def list_cluster_templates(self) -> ClusterTemplateListResponse:
        try:
            req: ListClusterTemplatesRequestDTO = ListClusterTemplatesRequestDTO(
                api=ManagementApi(self.api_client)
            )
            return self.execute_command(ListClusterTemplatesCommand(request=req))
        except ApiException as e:
            raise ServiceError(
                f"api error while fetching cluster templates. "
                f"Error code: {e.status}, error body: {e.body}"
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while fetching cluster templates: {e}"
            )

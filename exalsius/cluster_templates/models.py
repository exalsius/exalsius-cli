from exalsius_api_client.api.management_api import ManagementApi
from pydantic import Field

from exalsius.core.base.models import BaseRequestDTO


class ClusterTemplatesRequestDTO(BaseRequestDTO):
    api: ManagementApi = Field(..., description="The API client")


class ListClusterTemplatesRequestDTO(ClusterTemplatesRequestDTO):
    pass

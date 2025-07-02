from typing import Optional, Tuple

import exalsius_api_client
from exalsius_api_client import WorkspacesApi
from exalsius_api_client.models.error import Error as ExalsiusError
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse
from exalsius_api_client.rest import ApiException

from exalsius.core.operations.base import ListOperation


class ListWorkspacesOperation(ListOperation[WorkspacesListResponse]):
    def __init__(self, api_client: exalsius_api_client.ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[WorkspacesListResponse, Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspaces_list_response: WorkspacesListResponse = (
                api_instance.list_workspaces(cluster_id=self.cluster_id)
            )
            return workspaces_list_response, None
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, str(e)

from typing import List, Optional, Tuple

import exalsius_api_client
from exalsius_api_client import ManagementApi
from exalsius_api_client.models.credentials import Credentials
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exalsius.core.operations.base import ListOperation


class ListCloudCredentialsOperation(ListOperation[Credentials]):
    def __init__(self, api_client: exalsius_api_client.ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[List[Credentials], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            credentials_list_response: CredentialsListResponse = (
                api_instance.list_credentials()
            )
        except Exception as e:
            return None, str(e)
        return credentials_list_response.credentials, None

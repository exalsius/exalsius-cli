from typing import Optional, Tuple

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exalsius.core.operations.base import BaseOperation


class ListCloudCredentialsOperation(BaseOperation[CredentialsListResponse]):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[Optional[CredentialsListResponse], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            credentials_list_response: CredentialsListResponse = (
                api_instance.list_credentials()
            )
            return credentials_list_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"

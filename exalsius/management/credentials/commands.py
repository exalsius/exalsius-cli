from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.management.credentials.models import ListCredentialsRequestDTO


class ListCredentialsCommand(
    ExalsiusAPICommand[
        ManagementApi, ListCredentialsRequestDTO, CredentialsListResponse
    ]
):
    def _execute_api_call(self) -> CredentialsListResponse:
        return self.api_client.list_credentials()

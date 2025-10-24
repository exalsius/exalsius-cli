from typing import Optional

from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exls.management.commons.commands import BaseManagementSdkCommand


class ListCredentialsSdkCommand(
    BaseManagementSdkCommand[None, CredentialsListResponse]
):
    def _execute_api_call(self, params: Optional[None]) -> CredentialsListResponse:
        response: CredentialsListResponse = self.api_client.list_credentials()
        return response

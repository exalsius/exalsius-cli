from typing import List, Optional

from exalsius_api_client.models.credentials import Credentials as SdkCredentials
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exls.management.commons.commands import BaseManagementSdkCommand
from exls.management.types.credentials.domain import (
    Credentials,
    CredentialsFilterParams,
)


def _create_credentials_from_sdk_model(sdk_model: SdkCredentials) -> Credentials:
    return Credentials(sdk_model=sdk_model)


class ListCredentialsSdkCommand(
    BaseManagementSdkCommand[CredentialsFilterParams, List[Credentials]]
):
    def _execute_api_call(
        self, params: Optional[CredentialsFilterParams]
    ) -> List[Credentials]:
        response: CredentialsListResponse = self.api_client.list_credentials()
        return [_create_credentials_from_sdk_model(c) for c in response.credentials]

from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.credentials import Credentials as SdkCredentials
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exls.management.types.credentials.domain import (
    Credentials,
)
from exls.management.types.credentials.gateway.base import CredentialsGateway
from exls.management.types.credentials.gateway.commands import (
    ListCredentialsSdkCommand,
)


class CredentialsGatewaySdk(CredentialsGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def _create_credentials_from_sdk_model(
        self, sdk_model: SdkCredentials
    ) -> Credentials:
        return Credentials(sdk_model=sdk_model)

    def list(self) -> List[Credentials]:
        command = ListCredentialsSdkCommand(self._management_api, params=None)
        response: CredentialsListResponse = command.execute()
        return [
            self._create_credentials_from_sdk_model(sdk_model=c)
            for c in response.credentials
        ]

from typing import List

from exalsius_api_client.api.management_api import ManagementApi

from exls.management.types.credentials.domain import (
    Credentials,
    CredentialsFilterParams,
)
from exls.management.types.credentials.gateway.base import CredentialsGateway
from exls.management.types.credentials.gateway.commands import (
    ListCredentialsSdkCommand,
)


class CredentialsGatewaySdk(CredentialsGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list(self, params: CredentialsFilterParams) -> List[Credentials]:
        command = ListCredentialsSdkCommand(self._management_api, params)
        response: List[Credentials] = command.execute()
        return response

from typing import List

from exalsius_api_client.api.management_api import ManagementApi

from exls.management.types.ssh_keys.domain import (
    AddSshKeyParams,
    SshKey,
    SshKeyFilterParams,
)
from exls.management.types.ssh_keys.gateway.base import SshKeysGateway
from exls.management.types.ssh_keys.gateway.commands import (
    AddSshKeySdkCommand,
    DeleteSshKeySdkCommand,
    ListSshKeysSdkCommand,
)


class SshKeysGatewaySdk(SshKeysGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list(self, params: SshKeyFilterParams) -> List[SshKey]:
        command = ListSshKeysSdkCommand(self._management_api, params)
        response: List[SshKey] = command.execute()
        return response

    def delete(self, ssh_key_id: str) -> str:
        command = DeleteSshKeySdkCommand(self._management_api, ssh_key_id)
        command.execute()
        return ssh_key_id

    def create(self, ssh_key_create_params: AddSshKeyParams) -> str:
        command = AddSshKeySdkCommand(self._management_api, ssh_key_create_params)
        response: str = command.execute()
        return response

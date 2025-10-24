from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner as SdkSshKey,
)

from exls.management.types.ssh_keys.domain import (
    SshKey,
)
from exls.management.types.ssh_keys.gateway.base import SshKeysGateway
from exls.management.types.ssh_keys.gateway.commands import (
    AddSshKeySdkCommand,
    DeleteSshKeySdkCommand,
    ListSshKeysSdkCommand,
)
from exls.management.types.ssh_keys.gateway.dtos import AddSshKeyParams


class SshKeysGatewaySdk(SshKeysGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def _create_ssh_key_from_sdk_model(self, sdk_model: SdkSshKey) -> SshKey:
        return SshKey(sdk_model=sdk_model)

    def list(self) -> List[SshKey]:
        command = ListSshKeysSdkCommand(self._management_api, params=None)
        response: SshKeysListResponse = command.execute()
        return [
            self._create_ssh_key_from_sdk_model(sdk_model=ssh_key)
            for ssh_key in response.ssh_keys
        ]

    def delete(self, ssh_key_id: str) -> str:
        command = DeleteSshKeySdkCommand(self._management_api, ssh_key_id)
        command.execute()
        return ssh_key_id

    def create(self, add_ssh_key_params: AddSshKeyParams) -> str:
        command = AddSshKeySdkCommand(
            self._management_api, params=add_ssh_key_params.to_sdk_request()
        )
        response: SshKeyCreateResponse = command.execute()
        return response.ssh_key_id

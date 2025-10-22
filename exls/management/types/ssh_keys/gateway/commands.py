from __future__ import annotations

import base64
from typing import List, Optional

from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner as SdkSshKey,
)

from exls.management.commons.commands import BaseManagementSdkCommand
from exls.management.types.ssh_keys.domain import (
    AddSshKeyParams,
    SshKey,
    SshKeyFilterParams,
)


def _create_ssh_key_from_sdk_model(sdk_model: SdkSshKey) -> SshKey:
    return SshKey(sdk_model=sdk_model)


class ListSshKeysSdkCommand(BaseManagementSdkCommand[SshKeyFilterParams, List[SshKey]]):
    def _execute_api_call(self, params: Optional[SshKeyFilterParams]) -> List[SshKey]:
        response: SshKeysListResponse = self.api_client.list_ssh_keys()
        return [
            _create_ssh_key_from_sdk_model(ssh_key) for ssh_key in response.ssh_keys
        ]


class AddSshKeySdkCommand(BaseManagementSdkCommand[AddSshKeyParams, str]):
    def _execute_api_call(self, params: Optional[AddSshKeyParams]) -> str:
        assert params is not None
        private_key_base64 = base64.b64encode(params.private_key.encode()).decode()
        request = SshKeyCreateRequest(
            name=params.name,
            private_key_b64=private_key_base64,
        )
        response: SshKeyCreateResponse = self.api_client.add_ssh_key(
            ssh_key_create_request=request
        )
        return response.ssh_key_id


class DeleteSshKeySdkCommand(BaseManagementSdkCommand[str, None]):
    def _execute_api_call(self, params: Optional[str]) -> None:
        assert params is not None
        return self.api_client.delete_ssh_key(params)

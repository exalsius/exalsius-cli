from __future__ import annotations

from typing import Optional

from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse

from exls.management.commons.commands import BaseManagementSdkCommand


class ListSshKeysSdkCommand(BaseManagementSdkCommand[None, SshKeysListResponse]):
    def _execute_api_call(self, params: Optional[None]) -> SshKeysListResponse:
        response: SshKeysListResponse = self.api_client.list_ssh_keys()
        return response


class AddSshKeySdkCommand(
    BaseManagementSdkCommand[SshKeyCreateRequest, SshKeyCreateResponse]
):
    def _execute_api_call(
        self, params: Optional[SshKeyCreateRequest]
    ) -> SshKeyCreateResponse:
        assert params is not None

        response: SshKeyCreateResponse = self.api_client.add_ssh_key(
            ssh_key_create_request=params
        )
        return response


class DeleteSshKeySdkCommand(BaseManagementSdkCommand[str, None]):
    def _execute_api_call(self, params: Optional[str]) -> None:
        assert params is not None
        self.api_client.delete_ssh_key(ssh_key_id=params)

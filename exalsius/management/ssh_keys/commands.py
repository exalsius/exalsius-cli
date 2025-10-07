from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.management.ssh_keys.models import (
    ListSshKeysRequestDTO,
    SSHKeysAddRequestDTO,
    SSHKeysDeleteRequestDTO,
)


class ListSshKeysCommand(
    ExalsiusAPICommand[ManagementApi, ListSshKeysRequestDTO, SshKeysListResponse]
):
    def _execute_api_call(self) -> SshKeysListResponse:
        return self.api_client.list_ssh_keys()


class AddSSHKeyCommand(
    ExalsiusAPICommand[ManagementApi, SSHKeysAddRequestDTO, SshKeyCreateResponse]
):
    def _execute_api_call(self) -> SshKeyCreateResponse:
        return self.api_client.add_ssh_key(
            SshKeyCreateRequest(
                name=self.request.name,
                private_key_b64=self.request.private_key_base64,
            )
        )


class DeleteSSHKeyCommand(
    ExalsiusAPICommand[ManagementApi, SSHKeysDeleteRequestDTO, None]
):
    def _execute_api_call(self) -> None:
        return self.api_client.delete_ssh_key(self.request.id)

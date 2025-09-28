from typing import List

from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.core.base.commands import BaseCommand
from exalsius.management.ssh_keys.models import (
    ListSshKeysRequestDTO,
    SSHKeysAddRequestDTO,
    SSHKeysDeleteRequestDTO,
)


class ListSshKeysCommand(BaseCommand):
    def __init__(self, request: ListSshKeysRequestDTO):
        self.request: ListSshKeysRequestDTO = request

    def execute(self) -> List[SshKeysListResponseSshKeysInner]:
        response: SshKeysListResponse = self.request.api.list_ssh_keys()
        return response.ssh_keys


class AddSSHKeyCommand(BaseCommand):
    def __init__(self, request: SSHKeysAddRequestDTO):
        self.request: SSHKeysAddRequestDTO = request

    def execute(self) -> SshKeyCreateResponse:
        return self.request.api.add_ssh_key(
            SshKeyCreateRequest(
                name=self.request.name,
                private_key_b64=self.request.private_key_base64,
            )
        )


class DeleteSSHKeyCommand(BaseCommand):
    def __init__(self, request: SSHKeysDeleteRequestDTO):
        self.request: SSHKeysDeleteRequestDTO = request

    def execute(self) -> None:
        self.request.api.delete_ssh_key(self.request.id)

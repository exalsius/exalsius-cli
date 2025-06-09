import pathlib
from typing import List, Optional, Tuple

from exalsius_api_client.models.ssh_key import SshKey
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse

from exalsius.core.operations.ssh_key_operations import (
    AddSSHKeyOperation,
    DeleteSSHKeyOperation,
    ListSSHKeysOperation,
)
from exalsius.core.services.base import BaseService


class SSHKeyService(BaseService):
    def add_ssh_key(
        self, name: str, key_path: pathlib.Path
    ) -> Tuple[SshKeyCreateResponse, Optional[str]]:
        if not key_path.exists():
            return None, f"SSH key file {key_path} does not exist"

        if not key_path.is_file():
            return None, f"SSH key file {key_path} is not a file"

        return self.execute_operation(
            AddSSHKeyOperation(
                self.api_client,
                name,
                key_path,
            )
        )

    def list_ssh_keys(self) -> Tuple[List[SshKey], Optional[str]]:
        return self.execute_operation(
            ListSSHKeysOperation(
                self.api_client,
            )
        )

    def delete_ssh_key(self, name: str) -> Tuple[bool, Optional[str]]:
        return self.execute_operation(
            DeleteSSHKeyOperation(
                self.api_client,
                name,
            )
        )

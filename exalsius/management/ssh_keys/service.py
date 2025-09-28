import base64
from pathlib import Path
from typing import Any, List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.management.ssh_keys.commands import (
    AddSSHKeyCommand,
    DeleteSSHKeyCommand,
    ListSshKeysCommand,
)
from exalsius.management.ssh_keys.models import (
    ListSshKeysRequestDTO,
    SSHKeysAddRequestDTO,
    SSHKeysDeleteRequestDTO,
)

SSH_KEYS_API_ERROR_TYPE: str = "SshKeysApiError"


class SshKeysService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def _execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=SSH_KEYS_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=SSH_KEYS_API_ERROR_TYPE,
            )

    def list_ssh_keys(self) -> List[SshKeysListResponseSshKeysInner]:
        req: ListSshKeysRequestDTO = ListSshKeysRequestDTO(
            api=ManagementApi(self.api_client)
        )
        return self._execute_command(ListSshKeysCommand(request=req))

    def add_ssh_key(self, name: str, key_path: Path) -> str:
        if not (key_path.exists() and key_path.is_file()):
            raise ServiceError(
                f"SSH key file {key_path} does not exist or is not a file"
            )

        # TODO: Move this to command
        try:
            with open(key_path, "rb") as key_file:
                private_key: bytes = key_file.read()
        except FileNotFoundError:
            raise ServiceError(f"SSH key file {key_path} does not exist")
        except Exception as e:
            raise ServiceError(f"Failed to read SSH key file {key_path}: {e}")

        req: SSHKeysAddRequestDTO = SSHKeysAddRequestDTO(
            api=ManagementApi(self.api_client),
            name=name,
            private_key_base64=base64.b64encode(private_key).decode(),
        )

        response: SshKeyCreateResponse = self._execute_command(
            AddSSHKeyCommand(request=req)
        )
        return response.ssh_key_id

    def delete_ssh_key(self, id: str) -> None:
        req: SSHKeysDeleteRequestDTO = SSHKeysDeleteRequestDTO(
            api=ManagementApi(self.api_client),
            id=id,
        )
        self._execute_command(DeleteSSHKeyCommand(request=req))

import base64
from typing import List, Optional, Tuple

import exalsius_api_client
from exalsius_api_client import ManagementApi
from exalsius_api_client.models.error import Error as ExalsiusError
from exalsius_api_client.models.ssh_key import SshKey
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.rest import ApiException

from exalsius.core.operations.base import BaseOperation, BooleanOperation, ListOperation


class ListSSHKeysOperation(ListOperation[SshKey]):
    def __init__(self, api_client: exalsius_api_client.ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[List[SshKey], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            ssh_keys_list_response: SshKeysListResponse = api_instance.list_ssh_keys()
        except Exception as e:
            return None, str(e)
        return ssh_keys_list_response.ssh_keys, None


class AddSSHKeyOperation(BaseOperation[SshKeyCreateResponse]):
    def __init__(
        self, api_client: exalsius_api_client.ApiClient, name: str, key_path: str
    ):
        self.api_client = api_client
        self.name = name
        self.key_path = key_path

    def execute(self) -> Tuple[SshKey, Optional[str]]:
        api_instance = ManagementApi(self.api_client)

        with open(self.key_path, "r") as key_file:
            private_key = key_file.read()

        private_key_b64 = base64.b64encode(private_key.encode()).decode()

        try:
            ssh_key_create_request = SshKeyCreateRequest(
                name=self.name, private_key_b64=private_key_b64
            )
            ssh_key_create_response: SshKeyCreateResponse = api_instance.add_ssh_key(
                ssh_key_create_request
            )
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

        return ssh_key_create_response, None


class DeleteSSHKeyOperation(BooleanOperation):
    def __init__(self, api_client: exalsius_api_client.ApiClient, name: str):
        self.api_client = api_client
        self.name = name

    def execute(self) -> Tuple[bool, Optional[str]]:
        api_instance = ManagementApi(self.api_client)

        # we first have to find the ssh key by name
        # TODO: for this we should probably adjust or add an extra endpoint
        ssh_keys, error = ListSSHKeysOperation(self.api_client).execute()
        if error:
            return False, f"Failed to list SSH keys: {error}"

        ssh_key = next((key for key in ssh_keys if key.name == self.name), None)
        if not ssh_key:
            return False, f"SSH key with name '{self.name}' not found"

        try:
            _ = api_instance.delete_ssh_key(ssh_key.id)
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return False, error.detail
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
        return True, None

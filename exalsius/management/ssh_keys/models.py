from pydantic import Field

from exalsius.management.models import BaseManagementRequestDTO


class SSHKeysListRequestDTO(BaseManagementRequestDTO):
    pass


class SSHKeysAddRequestDTO(BaseManagementRequestDTO):
    name: str = Field(..., description="The name of the SSH key")
    private_key_base64: str = Field(..., description="The base64 encoded private key")


class SSHKeysDeleteRequestDTO(BaseManagementRequestDTO):
    id: str = Field(..., description="The ID of the SSH key")


class ListSshKeysRequestDTO(BaseManagementRequestDTO):
    pass

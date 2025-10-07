from pydantic import Field

from exalsius.core.base.commands import BaseRequestDTO


class SSHKeysListRequestDTO(BaseRequestDTO):
    pass


class SSHKeysAddRequestDTO(BaseRequestDTO):
    name: str = Field(..., description="The name of the SSH key")
    private_key_base64: str = Field(..., description="The base64 encoded private key")


class SSHKeysDeleteRequestDTO(BaseRequestDTO):
    id: str = Field(..., description="The ID of the SSH key")


class ListSshKeysRequestDTO(BaseRequestDTO):
    pass

from pydantic import Field

from exalsius.core.base.commands import BaseRequest


class SSHKeysListRequestDTO(BaseRequest):
    pass


class SSHKeysAddRequestDTO(BaseRequest):
    name: str = Field(..., description="The name of the SSH key")
    private_key_base64: str = Field(..., description="The base64 encoded private key")


class SSHKeysDeleteRequestDTO(BaseRequest):
    id: str = Field(..., description="The ID of the SSH key")


class ListSshKeysRequestDTO(BaseRequest):
    pass

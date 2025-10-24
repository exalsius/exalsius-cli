from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from pydantic import BaseModel, Field, StrictStr


class AddSshKeyParams(BaseModel):
    name: StrictStr = Field(..., description="The name of the SSH key")
    private_key_base64: StrictStr = Field(..., description="The private key")

    def to_sdk_request(self) -> SshKeyCreateRequest:
        return SshKeyCreateRequest(
            name=self.name,
            private_key_b64=self.private_key_base64,
        )

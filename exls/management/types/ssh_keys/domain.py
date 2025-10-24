from __future__ import annotations

from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner as SdkSshKey,
)
from pydantic import BaseModel, Field, StrictStr


class SshKey(BaseModel):
    sdk_model: SdkSshKey = Field(..., description="The SDK model of the SSH key")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def name(self) -> StrictStr:
        if self.sdk_model.name is None:
            raise ValueError("Name is None")
        return self.sdk_model.name

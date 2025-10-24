from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, StrictStr

from exls.management.types.ssh_keys.domain import SshKey


class ListSshKeysRequestDTO(BaseModel):
    pass


class SshKeyDTO(BaseModel):
    id: StrictStr
    name: StrictStr

    @classmethod
    def from_domain(cls, domain_obj: SshKey) -> SshKeyDTO:
        return cls(
            id=domain_obj.id,
            name=domain_obj.name,
        )


class AddSshKeyRequestDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the SSH key")
    key_path: Path = Field(..., description="The path to the SSH key file")

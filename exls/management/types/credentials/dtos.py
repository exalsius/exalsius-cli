from __future__ import annotations

from pydantic import BaseModel

from exls.management.types.credentials.domain import Credentials


class ListCredentialsRequestDTO(BaseModel):
    pass


class CredentialsDTO(BaseModel):
    name: str
    description: str

    @classmethod
    def from_domain(cls, domain_obj: Credentials) -> CredentialsDTO:
        return cls(
            name=domain_obj.name,
            description=domain_obj.description,
        )

from abc import ABC, abstractmethod
from typing import List

from exls.management.types.ssh_keys.domain import (
    AddSshKeyParams,
    SshKey,
    SshKeyFilterParams,
)


class SshKeysGateway(ABC):
    @abstractmethod
    def list(self, params: SshKeyFilterParams) -> List[SshKey]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, ssh_key_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create(self, ssh_key_create_params: AddSshKeyParams) -> str:
        raise NotImplementedError

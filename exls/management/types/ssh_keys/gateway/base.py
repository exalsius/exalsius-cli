from abc import ABC, abstractmethod
from typing import List

from exls.management.types.ssh_keys.domain import (
    SshKey,
)
from exls.management.types.ssh_keys.gateway.dtos import AddSshKeyParams


class SshKeysGateway(ABC):
    @abstractmethod
    def list(self) -> List[SshKey]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, ssh_key_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create(self, add_ssh_key_params: AddSshKeyParams) -> str:
        raise NotImplementedError

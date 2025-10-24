from abc import ABC, abstractmethod
from typing import List

from exls.management.types.credentials.domain import (
    Credentials,
)


class CredentialsGateway(ABC):
    @abstractmethod
    def list(self) -> List[Credentials]:
        raise NotImplementedError

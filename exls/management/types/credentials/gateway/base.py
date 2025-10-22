from abc import ABC, abstractmethod
from typing import List

from exls.management.types.credentials.domain import (
    Credentials,
    CredentialsFilterParams,
)


class CredentialsGateway(ABC):
    @abstractmethod
    def list(self, params: CredentialsFilterParams) -> List[Credentials]:
        raise NotImplementedError

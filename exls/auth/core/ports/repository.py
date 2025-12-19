from abc import ABC, abstractmethod

from exls.auth.core.domain import (
    LoadedToken,
    StoreTokenRequest,
)
from exls.shared.core.domain import ExalsiusError


class TokenRepositoryError(ExalsiusError):
    pass


class TokenRepository(ABC):
    @abstractmethod
    def store(self, request: StoreTokenRequest) -> None: ...

    @abstractmethod
    def load(self, client_id: str) -> LoadedToken: ...

    @abstractmethod
    def delete(self, client_id: str) -> None: ...

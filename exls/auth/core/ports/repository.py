from abc import ABC, abstractmethod

from exls.auth.core.domain import (
    LoadedToken,
    Token,
)
from exls.shared.core.exceptions import ExalsiusError


class TokenRepositoryError(ExalsiusError):
    pass


class TokenRepository(ABC):
    @abstractmethod
    def store(self, token: Token) -> None: ...

    @abstractmethod
    def load(self, client_id: str) -> LoadedToken: ...

    @abstractmethod
    def delete(self, client_id: str) -> None: ...

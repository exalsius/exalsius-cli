from abc import ABC, abstractmethod

from exls.auth.core.domain import (
    DeviceCode,
    Token,
    TokenExpiryMetadata,
    User,
)
from exls.shared.core.exceptions import ExalsiusError


class AuthError(ExalsiusError):
    pass


class AuthOperations(ABC):
    @abstractmethod
    def get_client_id(self) -> str: ...

    @abstractmethod
    def fetch_device_code(self) -> DeviceCode: ...

    @abstractmethod
    def poll_for_authentication(
        self,
        device_code: DeviceCode,
    ) -> Token: ...

    @abstractmethod
    def decode_token_expiry_metadata(self, token: str) -> TokenExpiryMetadata: ...

    @abstractmethod
    def decode_user_from_token(self, id_token: str) -> User: ...

    @abstractmethod
    def validate_token(self, id_token: str) -> User: ...

    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> Token: ...

    @abstractmethod
    def revoke_token(self, token: str) -> None: ...

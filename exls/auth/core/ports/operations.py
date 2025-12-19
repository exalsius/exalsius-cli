from abc import ABC, abstractmethod

from exls.auth.core.domain import (
    AuthenticationRequest,
    DeviceCode,
    FetchDeviceCodeRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    Token,
    TokenExpiryMetadata,
    User,
    ValidateTokenRequest,
)
from exls.shared.core.domain import ExalsiusError


class AuthError(ExalsiusError):
    pass


class AuthOperations(ABC):
    @abstractmethod
    def fetch_device_code(self, request: FetchDeviceCodeRequest) -> DeviceCode: ...

    @abstractmethod
    def poll_for_authentication(
        self,
        request: AuthenticationRequest,
    ) -> Token: ...

    @abstractmethod
    def load_token_expiry_metadata(self, token: str) -> TokenExpiryMetadata: ...

    @abstractmethod
    def validate_token(self, request: ValidateTokenRequest) -> User: ...

    @abstractmethod
    def refresh_access_token(self, request: RefreshTokenRequest) -> Token: ...

    @abstractmethod
    def revoke_token(self, request: RevokeTokenRequest) -> None: ...

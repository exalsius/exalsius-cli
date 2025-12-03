from abc import ABC, abstractmethod

from exls.auth.core.domain import (
    AuthenticationRequest,
    DeviceCode,
    FetchDeviceCodeRequest,
    LoadedToken,
    RefreshTokenRequest,
    RevokeTokenRequest,
    StoreTokenRequest,
    Token,
    TokenExpiryMetadata,
    User,
    ValidateTokenRequest,
)
from exls.shared.core.domain import ExalsiusError


class AuthGatewayError(ExalsiusError):
    pass


class TokenStorageError(ExalsiusError):
    pass


class IAuthGateway(ABC):
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


class ITokenStorageGateway(ABC):
    @abstractmethod
    def store_token(self, request: StoreTokenRequest) -> None: ...

    @abstractmethod
    def load_token(self, client_id: str) -> LoadedToken: ...

    @abstractmethod
    def clear_token(self, client_id: str) -> None: ...

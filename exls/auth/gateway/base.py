from abc import ABC, abstractmethod

from exls.auth.domain import (
    DeviceCode,
    LoadedToken,
    Token,
    User,
)
from exls.auth.gateway.dtos import (
    Auth0AuthenticationParams,
    Auth0FetchDeviceCodeParams,
    Auth0RefreshTokenParams,
    Auth0RevokeTokenParams,
    Auth0ValidateTokenParams,
    StoreTokenOnKeyringParams,
)


class AuthGateway(ABC):
    @abstractmethod
    def fetch_device_code(self, params: Auth0FetchDeviceCodeParams) -> DeviceCode:
        pass

    @abstractmethod
    def poll_for_authentication(
        self,
        params: Auth0AuthenticationParams,
    ) -> Token:
        pass

    @abstractmethod
    def validate_token(self, params: Auth0ValidateTokenParams) -> User:
        pass

    @abstractmethod
    def refresh_access_token(self, params: Auth0RefreshTokenParams) -> Token:
        pass

    @abstractmethod
    def revoke_token(self, params: Auth0RevokeTokenParams) -> None:
        pass


class TokenStorageGateway(ABC):
    @abstractmethod
    def store_token(self, params: StoreTokenOnKeyringParams) -> None:
        pass

    @abstractmethod
    def load_token(self, client_id: str) -> LoadedToken:
        pass

    @abstractmethod
    def clear_token(self, client_id: str) -> None:
        pass

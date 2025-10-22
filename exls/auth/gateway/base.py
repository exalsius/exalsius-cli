from abc import ABC, abstractmethod

from exls.auth.domain import (
    DeviceCode,
    FetchDeviceCodeParams,
    LoadedToken,
    PollForAuthenticationParams,
    RefreshTokenParams,
    RevokeTokenParams,
    Token,
    User,
    ValidateTokenParams,
)


class AuthGateway(ABC):
    @abstractmethod
    def fetch_device_code(self, params: FetchDeviceCodeParams) -> DeviceCode:
        pass

    @abstractmethod
    def poll_for_authentication(
        self,
        params: PollForAuthenticationParams,
    ) -> Token:
        pass

    @abstractmethod
    def validate_token(self, params: ValidateTokenParams) -> User:
        pass

    @abstractmethod
    def refresh_access_token(self, params: RefreshTokenParams) -> Token:
        pass

    @abstractmethod
    def revoke_token(self, params: RevokeTokenParams) -> None:
        pass


class TokenStorageGateway(ABC):
    @abstractmethod
    def store_token(self, token: Token) -> None:
        pass

    @abstractmethod
    def load_token(self, client_id: str) -> LoadedToken:
        pass

    @abstractmethod
    def clear_token(self, loaded_token: LoadedToken) -> None:
        pass

import logging
from typing import Callable

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
from exls.auth.dtos import (
    AcquiredAccessTokenDTO,
    DeviceCodeAuthenticationDTO,
    RefreshTokenRequestDTO,
    UserInfoDTO,
)
from exls.auth.gateway.base import AuthGateway, TokenStorageGateway
from exls.config import AppConfig, Auth0Config
from exls.core.base.service import ServiceError, ServiceWarning
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory

logger = logging.getLogger(__name__)


class NotLoggedInWarning(ServiceWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class Auth0Service:
    def __init__(
        self,
        config: AppConfig,
        auth_gateway: AuthGateway,
        token_storage_gateway: TokenStorageGateway,
    ):
        self.auth_gateway: AuthGateway = auth_gateway
        self.token_storage_gateway: TokenStorageGateway = token_storage_gateway
        self.auth0_config: Auth0Config = config.auth0

    def _fetch_device_code(self) -> DeviceCode:
        params = FetchDeviceCodeParams.from_config(self.auth0_config)

        device_code: DeviceCode = self.auth_gateway.fetch_device_code(
            params=params,
        )
        return device_code

    def _poll_for_authentication(self, device_code: DeviceCode) -> Token:
        params: PollForAuthenticationParams = (
            PollForAuthenticationParams.from_device_code_and_config(
                device_code=device_code,
                config=self.auth0_config,
            )
        )

        token: Token = self.auth_gateway.poll_for_authentication(
            params=params,
        )
        return token

    def _validate_token(self, token: Token) -> User:
        params: ValidateTokenParams = ValidateTokenParams.from_token_and_config(
            token=token,
            config=self.auth0_config,
        )
        user: User = self.auth_gateway.validate_token(params=params)
        return user

    @handle_service_errors("logging in")
    def login(
        self,
        display_device_code_handler: Callable[[DeviceCodeAuthenticationDTO], None],
    ) -> UserInfoDTO:
        try:
            # 1. Fetch the device code.
            device_code: DeviceCode = self._fetch_device_code()

            # 2. Display the device code to the user.
            display_device_code_handler(
                DeviceCodeAuthenticationDTO.from_domain(device_code)
            )

            # 3. Poll for the authentication response.
            token: Token = self._poll_for_authentication(device_code)

            # 4. Validate the token.
            user: User = self._validate_token(token)

            # 5. Store the token on the keyring.
            self.token_storage_gateway.store_token(token=token)

            return UserInfoDTO.from_domain(user=user, token=token)
        except KeyboardInterrupt:
            raise ServiceWarning("User cancelled authentication polling.")

    def _load_token_from_keyring(self) -> LoadedToken:
        loaded_token: LoadedToken = self.token_storage_gateway.load_token(
            self.auth0_config.client_id
        )
        return loaded_token

    def _refresh_access_token(self, params: RefreshTokenParams) -> UserInfoDTO:
        token: Token = self.auth_gateway.refresh_access_token(params=params)

        user: User = self._validate_token(token)

        self.token_storage_gateway.store_token(token=token)

        return UserInfoDTO.from_domain(token=token, user=user)

    @handle_service_errors("acquiring access token")
    def acquire_access_token(self) -> AcquiredAccessTokenDTO:
        loaded_token: LoadedToken = self._load_token_from_keyring()

        if loaded_token.is_expired:
            if not loaded_token.refresh_token:
                raise ServiceError("Session is expired. Please log in again.")

            try:
                params: RefreshTokenParams = (
                    RefreshTokenParams.from_refresh_token_request_and_config(
                        refresh_token_request=RefreshTokenRequestDTO(
                            refresh_token=loaded_token.refresh_token,
                        ),
                        config=self.auth0_config,
                    )
                )
                _ = self._refresh_access_token(params=params)
                return AcquiredAccessTokenDTO.from_loaded_token(
                    loaded_token=loaded_token
                )
            except ServiceError as e:
                raise ServiceError(
                    f"failed to refresh access token: {e.message}. Please log in again."
                ) from e
        else:
            return AcquiredAccessTokenDTO.from_loaded_token(loaded_token=loaded_token)

    def logout(self) -> None:
        try:
            loaded_token: LoadedToken = self._load_token_from_keyring()
        except ServiceError as e:
            raise NotLoggedInWarning(f"You are not logged in: {e.message}") from e

        try:
            self.auth_gateway.revoke_token(
                params=RevokeTokenParams.from_token_and_config(
                    token=loaded_token.access_token,
                    config=self.auth0_config,
                )
            )
        except ServiceError as e:
            raise ServiceWarning(f"failed to revoke token: {e.message}") from e
        finally:
            self.token_storage_gateway.clear_token(loaded_token=loaded_token)


def get_auth_service(config: AppConfig) -> Auth0Service:
    gateway_factory: GatewayFactory = GatewayFactory(config=config)
    auth_gateway: AuthGateway = gateway_factory.create_auth_gateway()
    token_storage_gateway: TokenStorageGateway = (
        gateway_factory.create_token_storage_gateway()
    )
    return Auth0Service(
        config=config,
        auth_gateway=auth_gateway,
        token_storage_gateway=token_storage_gateway,
    )

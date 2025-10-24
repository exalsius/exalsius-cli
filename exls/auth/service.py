import logging

from exls.auth.domain import (
    DeviceCode,
    LoadedToken,
    Token,
    User,
)
from exls.auth.dtos import (
    DeviceCodeAuthenticationDTO,
    UserInfoDTO,
)
from exls.auth.gateway.base import AuthGateway, TokenStorageGateway
from exls.auth.gateway.dtos import (
    Auth0AuthenticationParams,
    Auth0FetchDeviceCodeParams,
    Auth0RefreshTokenParams,
    Auth0ValidateTokenParams,
)
from exls.auth.gateway.errors import Auth0CommandError, KeyringCommandError
from exls.auth.gateway.mappers import (
    auth0_authentication_params_from_device_code_and_config,
    auth0_fetch_device_code_params_from_config,
    auth0_refresh_token_params_from_token_and_config,
    auth0_revoke_token_params_from_token_and_config,
    auth0_validate_token_params_from_access_token_and_config,
    store_token_params_from_token_and_config,
)
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
        params: Auth0FetchDeviceCodeParams = auth0_fetch_device_code_params_from_config(
            config=self.auth0_config
        )

        device_code: DeviceCode = self.auth_gateway.fetch_device_code(
            params=params,
        )
        return device_code

    def _poll_for_authentication(self, device_code: DeviceCode) -> Token:
        params: Auth0AuthenticationParams = (
            auth0_authentication_params_from_device_code_and_config(
                device_code=device_code,
                config=self.auth0_config,
            )
        )

        token: Token = self.auth_gateway.poll_for_authentication(
            params=params,
        )
        return token

    def _validate_token(self, id_token: str) -> User:
        params: Auth0ValidateTokenParams = (
            auth0_validate_token_params_from_access_token_and_config(
                id_token=id_token,
                config=self.auth0_config,
            )
        )
        user: User = self.auth_gateway.validate_token(params=params)
        return user

    @handle_service_errors("logging in")
    def initiate_device_code_login(self) -> DeviceCodeAuthenticationDTO:
        device_code: DeviceCode = self._fetch_device_code()
        return DeviceCodeAuthenticationDTO.from_domain(device_code)

    @handle_service_errors("polling for authentication")
    def poll_for_authentication(
        self, device_code_dto: DeviceCodeAuthenticationDTO
    ) -> UserInfoDTO:
        try:
            device_code = DeviceCode(
                verification_uri=device_code_dto.verification_uri,
                verification_uri_complete=device_code_dto.verification_uri_complete,
                user_code=device_code_dto.user_code,
                device_code=device_code_dto.device_code,
                expires_in=device_code_dto.expires_in,
                interval=self.auth0_config.device_code_poll_interval_seconds,
            )
            token: Token = self._poll_for_authentication(device_code)
            user: User = self._validate_token(token.id_token)
            self.token_storage_gateway.store_token(
                params=store_token_params_from_token_and_config(
                    token=token,
                    config=self.auth0_config,
                )
            )
            return UserInfoDTO.from_token_domain(user=user, token=token)
        except KeyboardInterrupt:
            raise ServiceWarning("User cancelled authentication polling.")

    def _load_token_from_keyring(self) -> LoadedToken:
        loaded_token: LoadedToken = self.token_storage_gateway.load_token(
            self.auth0_config.client_id
        )
        return loaded_token

    def _refresh_access_token(self, loaded_token: LoadedToken) -> UserInfoDTO:
        params: Auth0RefreshTokenParams = (
            auth0_refresh_token_params_from_token_and_config(
                loaded_token=loaded_token,
                config=self.auth0_config,
            )
        )

        refreshed_token: Token = self.auth_gateway.refresh_access_token(params=params)

        user: User = self._validate_token(refreshed_token.id_token)

        self.token_storage_gateway.store_token(
            params=store_token_params_from_token_and_config(
                token=refreshed_token,
                config=self.auth0_config,
            )
        )

        return UserInfoDTO.from_token_domain(token=refreshed_token, user=user)

    @handle_service_errors("acquiring access token")
    def acquire_access_token(self) -> UserInfoDTO:
        try:
            loaded_token: LoadedToken = self._load_token_from_keyring()
        except KeyringCommandError as e:
            raise NotLoggedInWarning(f"You are not logged in: {e.message}") from e

        if loaded_token.is_expired:
            if not loaded_token.refresh_token:
                raise ServiceError("Session is expired. Please log in again.")

            try:
                user_info: UserInfoDTO = self._refresh_access_token(
                    loaded_token=loaded_token
                )
                return user_info
            except Auth0CommandError as e:
                raise ServiceError(
                    f"failed to refresh access token. Please log in again. Error: {e.message}"
                ) from e
        else:
            user: User = self._validate_token(loaded_token.id_token)
            return UserInfoDTO.from_loaded_token_domain(
                user=user, loaded_token=loaded_token
            )

    @handle_service_errors("logging out")
    def logout(self) -> None:
        try:
            loaded_token: LoadedToken = self._load_token_from_keyring()
        except KeyringCommandError as e:
            raise NotLoggedInWarning(f"You are not logged in: {e.message}") from e

        try:
            self.auth_gateway.revoke_token(
                params=auth0_revoke_token_params_from_token_and_config(
                    loaded_token=loaded_token,
                    config=self.auth0_config,
                )
            )
        except Exception as e:
            raise ServiceError(f"failed to revoke token: {e}") from e
        finally:
            self.token_storage_gateway.clear_token(client_id=loaded_token.client_id)


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

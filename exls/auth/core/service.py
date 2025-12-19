from exls.auth.core.domain import (
    AuthenticationRequest,
    AuthSession,
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
from exls.auth.core.ports.operations import AuthError, AuthOperations
from exls.auth.core.ports.repository import TokenRepository, TokenRepositoryError
from exls.config import AuthConfig
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.core.service import ServiceError, ServiceWarning

# TODO: We have a tight coupling between auth0 and the auth domain service logic
#       This should be decoupled by moving the auth0 specific logic to the auth0 adapter;
#       including the configuration.


class NotLoggedInWarning(ServiceWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class AuthService:
    def __init__(
        self,
        auth_config: AuthConfig,
        auth_operations: AuthOperations,
        token_repository: TokenRepository,
    ):
        self._auth_operations: AuthOperations = auth_operations
        self._token_repository: TokenRepository = token_repository
        self._auth_config: AuthConfig = auth_config

    def _create_fetch_device_code_request(self) -> FetchDeviceCodeRequest:
        return FetchDeviceCodeRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            audience=self._auth_config.audience,
            scope=self._auth_config.scope,
            algorithms=self._auth_config.algorithms,
        )

    def _create_authentication_request(
        self, device_code: DeviceCode
    ) -> AuthenticationRequest:
        return AuthenticationRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            device_code=device_code.device_code,
            grant_type=self._auth_config.device_code_grant_type,
            poll_interval_seconds=self._auth_config.device_code_poll_interval_seconds,
            poll_timeout_seconds=self._auth_config.device_code_poll_timeout_seconds,
            retry_limit=self._auth_config.device_code_retry_limit,
        )

    def _create_validate_token_request(self, id_token: str) -> ValidateTokenRequest:
        return ValidateTokenRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            id_token=id_token,
            leeway=self._auth_config.leeway,
        )

    def _create_refresh_token_request(
        self, loaded_token: LoadedToken
    ) -> RefreshTokenRequest:
        assert loaded_token.refresh_token is not None
        return RefreshTokenRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            refresh_token=loaded_token.refresh_token,
            scope=" ".join(self._auth_config.scope) if self._auth_config.scope else "",
        )

    def _create_revoke_token_request(
        self, loaded_token: LoadedToken
    ) -> RevokeTokenRequest:
        return RevokeTokenRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            token=loaded_token.access_token,
        )

    def _create_store_token_request(self, token: Token) -> StoreTokenRequest:
        return StoreTokenRequest(
            client_id=self._auth_config.client_id,
            domain=self._auth_config.domain,
            access_token=token.access_token,
            id_token=token.id_token,
            expires_in=token.expires_in,
            refresh_token=token.refresh_token,
            expiry=token.expiry,
        )

    def _fetch_device_code(self) -> DeviceCode:
        request = self._create_fetch_device_code_request()
        device_code: DeviceCode = self._auth_operations.fetch_device_code(
            request=request
        )
        return device_code

    def _poll_for_authentication(self, device_code: DeviceCode) -> Token:
        request = self._create_authentication_request(device_code)
        token: Token = self._auth_operations.poll_for_authentication(request=request)
        return token

    def _validate_token(self, id_token: str) -> User:
        request = self._create_validate_token_request(id_token)
        user: User = self._auth_operations.validate_token(request=request)
        return user

    @handle_service_layer_errors("logging in")
    def initiate_device_code_login(self) -> DeviceCode:
        return self._fetch_device_code()

    @handle_service_layer_errors("polling for authentication")
    def poll_for_authentication(self, device_code_input: DeviceCode) -> AuthSession:
        try:
            # We need to ensure we use the config interval, but respect the device_code properties
            device_code = DeviceCode(
                verification_uri=device_code_input.verification_uri,
                verification_uri_complete=device_code_input.verification_uri_complete,
                user_code=device_code_input.user_code,
                device_code=device_code_input.device_code,
                expires_in=device_code_input.expires_in,
                interval=self._auth_config.device_code_poll_interval_seconds,
            )
            token: Token = self._poll_for_authentication(device_code)
            user: User = self._validate_token(token.id_token)
            token_expiry_metadata: TokenExpiryMetadata = (
                self._auth_operations.load_token_expiry_metadata(token=token.id_token)
            )
            token.expires_in = token_expiry_metadata.expires_in

            store_request = self._create_store_token_request(token)
            self._token_repository.store(request=store_request)

            # Construct LoadedToken for the session return (as it was just stored/validated)
            loaded_token = LoadedToken(
                client_id=token.client_id,
                access_token=token.access_token,
                id_token=token.id_token,
                refresh_token=token.refresh_token,
                expiry=token_expiry_metadata.exp,
            )

            return AuthSession(user=user, token=loaded_token)
        except KeyboardInterrupt:
            raise ServiceWarning("User cancelled authentication polling.")

    def _load_token_from_keyring(self) -> LoadedToken:
        loaded_token: LoadedToken = self._token_repository.load(
            self._auth_config.client_id
        )
        return loaded_token

    def _refresh_access_token(self, loaded_token: LoadedToken) -> AuthSession:
        request = self._create_refresh_token_request(loaded_token)
        refreshed_token: Token = self._auth_operations.refresh_access_token(
            request=request
        )
        user: User = self._validate_token(refreshed_token.id_token)

        store_request = self._create_store_token_request(refreshed_token)
        self._token_repository.store(request=store_request)

        new_loaded_token = LoadedToken(
            client_id=refreshed_token.client_id,
            access_token=refreshed_token.access_token,
            id_token=refreshed_token.id_token,
            refresh_token=refreshed_token.refresh_token,
            expiry=refreshed_token.expiry,
        )
        return AuthSession(user=user, token=new_loaded_token)

    @handle_service_layer_errors("acquiring access token")
    def acquire_access_token(self) -> AuthSession:
        try:
            loaded_token: LoadedToken = self._load_token_from_keyring()
        except TokenRepositoryError as e:
            raise NotLoggedInWarning(f"You are not logged in: {str(e)}") from e

        if loaded_token.is_expired:
            if not loaded_token.refresh_token:
                raise ServiceError("Session is expired. Please log in again.")

            try:
                return self._refresh_access_token(loaded_token=loaded_token)
            except AuthError as e:
                raise ServiceError(
                    f"failed to refresh access token. Please log in again. Error: {str(e)}"
                ) from e
        else:
            user: User = self._validate_token(loaded_token.id_token)
            return AuthSession(user=user, token=loaded_token)

    @handle_service_layer_errors("logging out")
    def logout(self) -> None:
        try:
            loaded_token: LoadedToken = self._load_token_from_keyring()
        except TokenRepositoryError as e:
            raise NotLoggedInWarning(f"You are not logged in: {str(e)}") from e

        try:
            request = self._create_revoke_token_request(loaded_token)
            self._auth_operations.revoke_token(request=request)
        except Exception as e:
            raise ServiceError(f"failed to revoke token: {e}") from e
        finally:
            self._token_repository.delete(client_id=loaded_token.client_id)

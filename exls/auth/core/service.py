from exls.auth.core.domain import (
    AuthSession,
    DeviceCode,
    LoadedToken,
    Token,
    TokenExpiryMetadata,
    User,
)
from exls.auth.core.ports.operations import AuthError, AuthOperations
from exls.auth.core.ports.repository import TokenRepository, TokenRepositoryError
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.core.exceptions import ServiceError, ServiceWarning


class NotLoggedInWarning(ServiceWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class AuthService:
    def __init__(
        self,
        auth_operations: AuthOperations,
        token_repository: TokenRepository,
    ):
        self._auth_operations: AuthOperations = auth_operations
        self._token_repository: TokenRepository = token_repository

    @handle_service_layer_errors("logging in")
    def initiate_device_code_login(self) -> DeviceCode:
        return self._auth_operations.fetch_device_code()

    @handle_service_layer_errors("polling for authentication")
    def poll_for_authentication(self, device_code: DeviceCode) -> AuthSession:
        try:
            token: Token = self._auth_operations.poll_for_authentication(device_code)
            user: User = self._auth_operations.validate_token(token.id_token)
            token_expiry_metadata: TokenExpiryMetadata = (
                self._auth_operations.load_token_expiry_metadata(token=token.id_token)
            )
            token.expires_in = token_expiry_metadata.expires_in

            self._token_repository.store(token=token)

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

    def _refresh_access_token(self, refresh_token: str) -> AuthSession:
        refreshed_token: Token = self._auth_operations.refresh_access_token(
            refresh_token=refresh_token
        )
        user: User = self._auth_operations.validate_token(
            id_token=refreshed_token.id_token
        )

        self._token_repository.store(token=refreshed_token)

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
            client_id: str = self._auth_operations.get_client_id()
            loaded_token: LoadedToken = self._token_repository.load(client_id=client_id)
        except TokenRepositoryError as e:
            raise NotLoggedInWarning(f"You are not logged in: {str(e)}") from e

        if loaded_token.is_expired:
            if not loaded_token.refresh_token:
                raise ServiceError("Session is expired. Please log in again.")

            try:
                return self._refresh_access_token(
                    refresh_token=loaded_token.refresh_token
                )
            except AuthError as e:
                raise ServiceError(
                    f"failed to refresh access token. Please log in again. Error: {str(e)}"
                ) from e
        else:
            user: User = self._auth_operations.validate_token(
                id_token=loaded_token.id_token
            )
            return AuthSession(user=user, token=loaded_token)

    @handle_service_layer_errors("logging out")
    def logout(self) -> None:
        try:
            client_id: str = self._auth_operations.get_client_id()
            loaded_token: LoadedToken = self._token_repository.load(client_id=client_id)
        except TokenRepositoryError as e:
            raise NotLoggedInWarning(f"You are not logged in: {str(e)}") from e

        try:
            self._auth_operations.revoke_token(token=loaded_token.access_token)
        except Exception as e:
            raise ServiceError(f"failed to revoke token: {e}") from e
        finally:
            self._token_repository.delete(client_id=loaded_token.client_id)

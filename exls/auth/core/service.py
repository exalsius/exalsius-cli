import logging
from typing import Optional

from exls.auth.core.domain import (
    AuthSession,
    DeviceCodeLoginState,
    LoadedToken,
    LoginFlowState,
    PkceLoginState,
    Token,
    TokenExpiryMetadata,
    User,
)
from exls.auth.core.ports.device_code_operations import DeviceCodeOperations
from exls.auth.core.ports.operations import AuthError, AuthOperations
from exls.auth.core.ports.pkce_operations import PkceOperations
from exls.auth.core.ports.repository import TokenRepository, TokenRepositoryError
from exls.shared.core.decorators import handle_service_layer_errors
from exls.shared.core.exceptions import ServiceError, ServiceWarning

logger = logging.getLogger(__name__)


class NotLoggedInWarning(ServiceWarning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class PkceTimeoutError(ServiceError):
    """Raised when PKCE callback times out. App layer can offer device code fallback."""

    pass


class AuthService:
    def __init__(
        self,
        auth_operations: AuthOperations,
        token_repository: TokenRepository,
        device_code_operations: DeviceCodeOperations,
        pkce_operations: Optional[PkceOperations] = None,
    ):
        self._auth_operations: AuthOperations = auth_operations
        self._token_repository: TokenRepository = token_repository
        self._device_code_operations: DeviceCodeOperations = device_code_operations
        self._pkce_operations: Optional[PkceOperations] = pkce_operations

    # --- Unified login flow ---

    @handle_service_layer_errors("initiating login")
    def initiate_login(self, force_device_code: bool = False) -> LoginFlowState:
        """Start login flow. Returns intermediate state for app layer to render."""
        if self._pkce_operations and not force_device_code:
            return self._initiate_pkce()
        return self._initiate_device_code()

    def _initiate_pkce(self) -> PkceLoginState:
        assert self._pkce_operations is not None
        port = self._pkce_operations.start_callback_server()
        redirect_uri = f"http://localhost:{port}/callback"
        session = self._pkce_operations.generate_pkce_session(redirect_uri)
        auth_url = self._pkce_operations.build_authorization_url(session)
        return PkceLoginState(auth_url=auth_url, session=session)

    def _initiate_device_code(self) -> DeviceCodeLoginState:
        device_code = self._device_code_operations.fetch_device_code()
        return DeviceCodeLoginState(device_code=device_code)

    @handle_service_layer_errors("completing login")
    def complete_login(self, state: LoginFlowState) -> AuthSession:
        """Complete login flow using the intermediate state."""
        if isinstance(state, PkceLoginState):
            return self._complete_pkce(state)
        return self._complete_device_code(state)

    def _complete_pkce(self, state: PkceLoginState) -> AuthSession:
        assert self._pkce_operations is not None
        try:
            browser_opened = self._pkce_operations.open_browser(state.auth_url)
            if not browser_opened:
                logger.warning("Browser did not open, user must navigate manually")

            code = self._pkce_operations.wait_for_callback(state.session)
            token = self._pkce_operations.exchange_code_for_token(code, state.session)
            return self._validate_and_store_token(token)
        except AuthError as e:
            if "timed out" in str(e).lower():
                raise PkceTimeoutError(str(e)) from e
            raise
        except KeyboardInterrupt:
            raise ServiceWarning("Authentication cancelled.")
        finally:
            self._pkce_operations.shutdown_callback_server()

    def _complete_device_code(self, state: DeviceCodeLoginState) -> AuthSession:
        try:
            token = self._device_code_operations.poll_for_authentication(
                state.device_code
            )
            return self._validate_and_store_token(token)
        except KeyboardInterrupt:
            raise ServiceWarning("User cancelled authentication polling.")

    def _validate_and_store_token(self, token: Token) -> AuthSession:
        """Shared: validate token, store in keyring, return AuthSession."""
        user: User = self._auth_operations.validate_token(token.id_token)
        token_expiry: TokenExpiryMetadata = (
            self._auth_operations.decode_token_expiry_metadata(token=token.id_token)
        )
        token.expires_in = token_expiry.expires_in
        self._token_repository.store(token=token)

        loaded_token = LoadedToken(
            client_id=token.client_id,
            access_token=token.access_token,
            id_token=token.id_token,
            refresh_token=token.refresh_token,
            expiry=token_expiry.exp,
        )
        return AuthSession(user=user, token=loaded_token)

    # --- Token lifecycle ---

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
            user: User = self._auth_operations.decode_user_from_token(
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

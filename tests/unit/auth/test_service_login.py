"""Unit tests for AuthService login flow (initiate_login / complete_login)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from exls.auth.core.domain import (
    AuthSession,
    DeviceCode,
    DeviceCodeLoginState,
    PkceLoginState,
    PkceSession,
    Token,
    TokenExpiryMetadata,
    User,
)
from exls.auth.core.ports.device_code_operations import DeviceCodeOperations
from exls.auth.core.ports.operations import AuthError, AuthOperations
from exls.auth.core.ports.pkce_operations import PkceOperations
from exls.auth.core.ports.repository import TokenRepository
from exls.auth.core.service import AuthService, PkceTimeoutError
from exls.shared.core.exceptions import ServiceError, ServiceWarning

# --- Fixtures ---


@pytest.fixture
def mock_auth_operations() -> Mock:
    return Mock(spec=AuthOperations)


@pytest.fixture
def mock_device_code_operations() -> Mock:
    return Mock(spec=DeviceCodeOperations)


@pytest.fixture
def mock_pkce_operations() -> Mock:
    return Mock(spec=PkceOperations)


@pytest.fixture
def mock_token_repository() -> Mock:
    return Mock(spec=TokenRepository)


@pytest.fixture
def token() -> Token:
    return Token(
        client_id="client-id",
        access_token="access-token",
        id_token="id-token",
        scope="openid profile",
        token_type="Bearer",
        refresh_token="refresh-token",
        expires_in=3600,
    )


@pytest.fixture
def user() -> User:
    return User(email="test@example.com", nickname="testuser", sub="user-123")


@pytest.fixture
def token_metadata() -> TokenExpiryMetadata:
    return TokenExpiryMetadata(
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + timedelta(seconds=3600),
    )


@pytest.fixture
def device_code() -> DeviceCode:
    return DeviceCode(
        verification_uri="http://verify",
        verification_uri_complete="http://verify/complete",
        user_code="ABCD-1234",
        device_code="device-code-123",
        expires_in=900,
    )


@pytest.fixture
def pkce_session() -> PkceSession:
    return PkceSession(
        code_verifier="a" * 64,
        state="test-state",
        nonce="test-nonce",
        redirect_uri="http://localhost:8999/callback",
    )


def _make_service(
    auth_ops: Mock,
    token_repo: Mock,
    device_code_ops: Mock,
    pkce_ops: Mock | None = None,
) -> AuthService:
    return AuthService(
        auth_operations=auth_ops,
        token_repository=token_repo,
        device_code_operations=device_code_ops,
        pkce_operations=pkce_ops,
    )


# --- initiate_login ---


class TestInitiateLogin:
    def test_returns_pkce_state_when_pkce_available(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        pkce_session: PkceSession,
    ):
        mock_pkce_operations.start_callback_server.return_value = 8999
        mock_pkce_operations.generate_pkce_session.return_value = pkce_session
        mock_pkce_operations.build_authorization_url.return_value = (
            "https://auth0.com/authorize?..."
        )

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )
        state = service.initiate_login()

        assert isinstance(state, PkceLoginState)
        assert state.auth_url == "https://auth0.com/authorize?..."
        assert state.session == pkce_session
        mock_pkce_operations.start_callback_server.assert_called_once()
        mock_pkce_operations.generate_pkce_session.assert_called_once_with(
            "http://localhost:8999/callback"
        )

    def test_returns_device_code_state_when_no_pkce(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        device_code: DeviceCode,
    ):
        mock_device_code_operations.fetch_device_code.return_value = device_code

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
        )
        state = service.initiate_login()

        assert isinstance(state, DeviceCodeLoginState)
        assert state.device_code == device_code

    def test_force_device_code_bypasses_pkce(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        device_code: DeviceCode,
    ):
        mock_device_code_operations.fetch_device_code.return_value = device_code

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )
        state = service.initiate_login(force_device_code=True)

        assert isinstance(state, DeviceCodeLoginState)
        mock_pkce_operations.start_callback_server.assert_not_called()

    def test_uses_actual_port_for_redirect_uri(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        pkce_session: PkceSession,
    ):
        # Server returns a fallback port
        mock_pkce_operations.start_callback_server.return_value = 9001
        mock_pkce_operations.generate_pkce_session.return_value = pkce_session
        mock_pkce_operations.build_authorization_url.return_value = "https://url"

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )
        service.initiate_login()

        mock_pkce_operations.generate_pkce_session.assert_called_once_with(
            "http://localhost:9001/callback"
        )


# --- complete_login (PKCE) ---


class TestCompletePkceLogin:
    def _setup_service(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        token: Token,
        user: User,
        token_metadata: TokenExpiryMetadata,
    ) -> AuthService:
        mock_auth_operations.validate_token.return_value = user
        mock_auth_operations.decode_token_expiry_metadata.return_value = token_metadata
        mock_pkce_operations.open_browser.return_value = True
        mock_pkce_operations.wait_for_callback.return_value = "auth-code"
        mock_pkce_operations.exchange_code_for_token.return_value = token

        return _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )

    def test_complete_pkce_success(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        token: Token,
        user: User,
        token_metadata: TokenExpiryMetadata,
        pkce_session: PkceSession,
    ):
        service = self._setup_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
            token,
            user,
            token_metadata,
        )

        state = PkceLoginState(
            auth_url="https://auth0.com/authorize", session=pkce_session
        )
        result = service.complete_login(state)

        assert isinstance(result, AuthSession)
        assert result.user == user
        assert result.token.access_token == "access-token"
        mock_pkce_operations.open_browser.assert_called_once()
        mock_pkce_operations.wait_for_callback.assert_called_once()
        mock_pkce_operations.exchange_code_for_token.assert_called_once()
        mock_token_repository.store.assert_called_once()
        mock_pkce_operations.shutdown_callback_server.assert_called_once()

    def test_timeout_raises_pkce_timeout_error(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        pkce_session: PkceSession,
    ):
        mock_pkce_operations.open_browser.return_value = True
        mock_pkce_operations.wait_for_callback.side_effect = AuthError(
            "PKCE authentication timed out waiting for browser callback"
        )

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )

        state = PkceLoginState(
            auth_url="https://auth0.com/authorize", session=pkce_session
        )
        with pytest.raises(PkceTimeoutError):
            service.complete_login(state)

        # Server must be shut down even on timeout
        mock_pkce_operations.shutdown_callback_server.assert_called_once()

    def test_keyboard_interrupt_raises_service_warning(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        pkce_session: PkceSession,
    ):
        mock_pkce_operations.open_browser.return_value = True
        mock_pkce_operations.wait_for_callback.side_effect = KeyboardInterrupt

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )

        state = PkceLoginState(
            auth_url="https://auth0.com/authorize", session=pkce_session
        )
        with pytest.raises(ServiceWarning, match="Authentication cancelled"):
            service.complete_login(state)

        mock_pkce_operations.shutdown_callback_server.assert_called_once()

    def test_shutdown_called_on_auth_error(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        pkce_session: PkceSession,
    ):
        mock_pkce_operations.open_browser.return_value = True
        mock_pkce_operations.wait_for_callback.side_effect = AuthError("State mismatch")

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
        )

        state = PkceLoginState(
            auth_url="https://auth0.com/authorize", session=pkce_session
        )
        with pytest.raises(ServiceError):
            service.complete_login(state)

        mock_pkce_operations.shutdown_callback_server.assert_called_once()

    def test_browser_failure_does_not_abort(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        mock_pkce_operations: Mock,
        token: Token,
        user: User,
        token_metadata: TokenExpiryMetadata,
        pkce_session: PkceSession,
    ):
        """When browser fails to open, flow continues (user navigates manually)."""
        service = self._setup_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
            mock_pkce_operations,
            token,
            user,
            token_metadata,
        )
        mock_pkce_operations.open_browser.return_value = False

        state = PkceLoginState(
            auth_url="https://auth0.com/authorize", session=pkce_session
        )
        result = service.complete_login(state)

        assert isinstance(result, AuthSession)


# --- complete_login (Device Code) ---


class TestCompleteDeviceCodeLogin:
    def test_complete_device_code_success(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        token: Token,
        user: User,
        token_metadata: TokenExpiryMetadata,
        device_code: DeviceCode,
    ):
        mock_device_code_operations.poll_for_authentication.return_value = token
        mock_auth_operations.validate_token.return_value = user
        mock_auth_operations.decode_token_expiry_metadata.return_value = token_metadata

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
        )

        state = DeviceCodeLoginState(device_code=device_code)
        result = service.complete_login(state)

        assert isinstance(result, AuthSession)
        assert result.user == user
        mock_device_code_operations.poll_for_authentication.assert_called_once_with(
            device_code
        )
        mock_token_repository.store.assert_called_once()

    def test_keyboard_interrupt_raises_service_warning(
        self,
        mock_auth_operations: Mock,
        mock_token_repository: Mock,
        mock_device_code_operations: Mock,
        device_code: DeviceCode,
    ):
        mock_device_code_operations.poll_for_authentication.side_effect = (
            KeyboardInterrupt
        )

        service = _make_service(
            mock_auth_operations,
            mock_token_repository,
            mock_device_code_operations,
        )

        state = DeviceCodeLoginState(device_code=device_code)
        with pytest.raises(ServiceWarning, match="User cancelled"):
            service.complete_login(state)

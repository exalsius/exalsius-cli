from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

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
from exls.auth.core.service import AuthService, NotLoggedInWarning
from exls.shared.core.exceptions import ServiceError, ServiceWarning


@pytest.fixture
def mock_auth_operations() -> Mock:
    return Mock(spec=AuthOperations)


@pytest.fixture
def mock_token_repository() -> Mock:
    return Mock(spec=TokenRepository)


@pytest.fixture
def auth_service(
    mock_auth_operations: Mock, mock_token_repository: Mock
) -> AuthService:
    return AuthService(mock_auth_operations, mock_token_repository)


def test_initiate_device_code_login(
    auth_service: AuthService, mock_auth_operations: Mock
):
    expected_device_code: DeviceCode = DeviceCode(
        verification_uri="http://verify",
        verification_uri_complete="http://verify/complete",
        user_code="ABCD-1234",
        device_code="device-code-123",
        expires_in=900,
    )
    mock_auth_operations.fetch_device_code.return_value = expected_device_code

    result = auth_service.initiate_device_code_login()

    assert result == expected_device_code
    mock_auth_operations.fetch_device_code.assert_called_once()


def test_initiate_device_code_login_failure(
    auth_service: AuthService, mock_auth_operations: Mock
):
    """Test that the decorator converts unexpected errors to ServiceError."""
    mock_auth_operations.fetch_device_code.side_effect = Exception("Network error")

    with pytest.raises(ServiceError, match="logging in"):
        auth_service.initiate_device_code_login()


def test_poll_for_authentication_success(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    device_code: DeviceCode = DeviceCode(
        verification_uri="http://verify",
        verification_uri_complete="http://verify/complete",
        user_code="ABCD-1234",
        device_code="device-code-123",
        expires_in=900,
    )

    token = Token(
        client_id="client-id",
        access_token="access-token",
        id_token="id-token",
        scope="scope",
        token_type="Bearer",
        refresh_token="refresh-token",
        expires_in=3600,
    )

    user = User(email="test@example.com", nickname="testuser", sub="user-123")

    expiry_time = datetime.now(timezone.utc) + timedelta(seconds=3600)
    token_metadata = TokenExpiryMetadata(
        iat=datetime.now(timezone.utc),
        exp=expiry_time,
    )

    mock_auth_operations.poll_for_authentication.return_value = token
    mock_auth_operations.validate_token.return_value = user
    mock_auth_operations.load_token_expiry_metadata.return_value = token_metadata

    session = auth_service.poll_for_authentication(device_code)

    assert isinstance(session, AuthSession)
    assert session.user == user
    assert session.token.access_token == token.access_token
    assert session.token.expiry == expiry_time

    mock_auth_operations.poll_for_authentication.assert_called_once_with(device_code)
    mock_auth_operations.validate_token.assert_called_once_with(token.id_token)
    mock_auth_operations.load_token_expiry_metadata.assert_called_once_with(
        token=token.id_token
    )
    mock_token_repository.store.assert_called_once()


def test_poll_for_authentication_validation_failure(
    auth_service: AuthService, mock_auth_operations: Mock
):
    """Test behavior when polling succeeds but token validation fails."""
    device_code = DeviceCode(
        verification_uri="uri",
        verification_uri_complete="uri_c",
        user_code="user",
        device_code="dev",
        expires_in=900,
    )
    token = Token(
        client_id="cid",
        access_token="acc",
        id_token="id",
        scope="scope",
        token_type="Bearer",
        refresh_token="ref",
        expires_in=3600,
    )

    mock_auth_operations.poll_for_authentication.return_value = token
    # Simulate validation failure
    mock_auth_operations.validate_token.side_effect = AuthError("Invalid signature")

    with pytest.raises(ServiceError, match="polling for authentication"):
        auth_service.poll_for_authentication(device_code)


def test_poll_for_authentication_keyboard_interrupt(
    auth_service: AuthService, mock_auth_operations: Mock
):
    device_code: DeviceCode = DeviceCode(
        verification_uri="http://verify",
        verification_uri_complete="http://verify/complete",
        user_code="ABCD-1234",
        device_code="device-code-123",
        expires_in=900,
    )
    mock_auth_operations.poll_for_authentication.side_effect = KeyboardInterrupt

    with pytest.raises(ServiceWarning, match="User cancelled authentication polling"):
        auth_service.poll_for_authentication(device_code)


def test_acquire_access_token_success_valid_token(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="access-token",
        id_token="id-token",
        refresh_token="refresh-token",
        expiry=expiry_time,
    )
    user: User = User(email="test@example.com", nickname="testuser", sub="user-123")

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    mock_auth_operations.decode_user_from_token.return_value = user

    session: AuthSession = auth_service.acquire_access_token()

    assert session.user == user
    assert session.token == loaded_token
    mock_token_repository.load.assert_called_once_with(client_id=client_id)
    mock_auth_operations.decode_user_from_token.assert_called_once_with(
        id_token=loaded_token.id_token
    )


def test_acquire_access_token_decode_failure(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    """Test when a stored token loads but fails local decoding."""
    client_id = "client-id"
    # Token valid for 1 hour
    loaded_token = LoadedToken(
        client_id=client_id,
        access_token="acc",
        id_token="id",
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    # Simulate local decode failure
    mock_auth_operations.decode_user_from_token.side_effect = AuthError(
        "Malformed token"
    )

    with pytest.raises(ServiceError, match="acquiring access token"):
        auth_service.acquire_access_token()


def test_acquire_access_token_not_logged_in(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    mock_auth_operations.get_client_id.return_value = "client-id"
    mock_token_repository.load.side_effect = TokenRepositoryError(
        "failed to load token"
    )

    with pytest.raises(NotLoggedInWarning, match="You are not logged in"):
        auth_service.acquire_access_token()


def test_acquire_access_token_expired_refresh_success(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    # Token expired 1 hour ago
    expiry_time: datetime = datetime.now(timezone.utc) - timedelta(hours=1)
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="expired-token",
        id_token="expired-id-token",
        refresh_token="valid-refresh-token",
        expiry=expiry_time,
    )

    new_token: Token = Token(
        client_id=client_id,
        access_token="new-access-token",
        id_token="new-id-token",
        scope="scope",
        token_type="Bearer",
        refresh_token="new-refresh-token",
        expires_in=3600,
    )
    user = User(email="test@example.com", nickname="testuser", sub="user-123")

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    mock_auth_operations.refresh_access_token.return_value = new_token
    mock_auth_operations.validate_token.return_value = user

    session: AuthSession = auth_service.acquire_access_token()

    assert session.user == user
    assert session.token.access_token == "new-access-token"
    mock_auth_operations.refresh_access_token.assert_called_once_with(
        refresh_token="valid-refresh-token"
    )
    mock_token_repository.store.assert_called_once()


def test_acquire_access_token_expired_no_refresh(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    expiry_time: datetime = datetime.now(timezone.utc) - timedelta(hours=1)
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="expired-token",
        id_token="expired-id-token",
        refresh_token=None,  # No refresh token
        expiry=expiry_time,
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token

    with pytest.raises(ServiceError, match="Session is expired. Please log in again."):
        auth_service.acquire_access_token()


def test_acquire_access_token_refresh_failed(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    expiry_time: datetime = datetime.now(timezone.utc) - timedelta(hours=1)
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="expired-token",
        id_token="expired-id-token",
        refresh_token="valid-refresh-token",
        expiry=expiry_time,
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    mock_auth_operations.refresh_access_token.side_effect = AuthError("Refresh failed")

    with pytest.raises(ServiceError, match="failed to refresh access token"):
        auth_service.acquire_access_token()


def test_logout_success(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="access-token",
        id_token="id-token",
        refresh_token="refresh-token",
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token

    auth_service.logout()

    mock_auth_operations.revoke_token.assert_called_once_with(token="access-token")
    mock_token_repository.delete.assert_called_once_with(client_id=client_id)


def test_logout_not_logged_in(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    mock_auth_operations.get_client_id.return_value = "client-id"
    mock_token_repository.load.side_effect = TokenRepositoryError("Not found")

    with pytest.raises(NotLoggedInWarning, match="You are not logged in"):
        auth_service.logout()


def test_logout_revocation_failed(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    client_id: str = "client-id"
    loaded_token: LoadedToken = LoadedToken(
        client_id=client_id,
        access_token="access-token",
        id_token="id-token",
        refresh_token="refresh-token",
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    mock_auth_operations.revoke_token.side_effect = Exception("Revocation error")

    with pytest.raises(ServiceError, match="failed to revoke token"):
        auth_service.logout()

    # Even if revocation failed, delete should be called (in finally block)
    mock_token_repository.delete.assert_called_once_with(client_id=client_id)


def test_logout_delete_failed(
    auth_service: AuthService, mock_auth_operations: Mock, mock_token_repository: Mock
):
    """Test that errors in the finally block (repo delete) are propagated."""
    client_id = "client-id"
    loaded_token = LoadedToken(
        client_id=client_id,
        access_token="acc",
        id_token="id",
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    mock_auth_operations.get_client_id.return_value = client_id
    mock_token_repository.load.return_value = loaded_token
    # Revocation works, but deletion fails
    mock_token_repository.delete.side_effect = Exception("Disk error")

    with pytest.raises(Exception, match="Disk error"):
        auth_service.logout()

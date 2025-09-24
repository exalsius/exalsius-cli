from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests
from auth0.exceptions import TokenValidationError

from exalsius.auth.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0PollForAuthenticationCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
    ClearTokenFromKeyringCommand,
    KeyringKeys,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exalsius.auth.models import (
    Auth0APIError,
    Auth0AuthenticationDTO,
    Auth0AuthenticationError,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0FetchDeviceCodeRequestDTO,
    Auth0PollForAuthenticationRequestDTO,
    Auth0RefreshTokenRequestDTO,
    Auth0RevokeTokenRequestDTO,
    Auth0RevokeTokenStatusDTO,
    Auth0UserInfoDTO,
    Auth0ValidateTokenRequestDTO,
    ClearTokenFromKeyringRequestDTO,
    KeyringError,
    LoadedTokenDTO,
    LoadTokenFromKeyringRequestDTO,
    StoreTokenOnKeyringRequestDTO,
    TokenKeyringStorageStatusDTO,
)


@patch("exalsius.core.commons.commands.requests.post")
class TestAuth0FetchDeviceCodeCommand:
    def test_execute_success(self, mock_post: MagicMock):
        request_dto = Auth0FetchDeviceCodeRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            audience="test_audience",
            scope=["openid", "profile", "email"],
            algorithms=["RS256"],
        )
        command = Auth0FetchDeviceCodeCommand(request_dto)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "test_user_code",
            "verification_uri": "https://test.domain/activate",
            "verification_uri_complete": "https://test.domain/activate?user_code=test_user_code",
            "expires_in": 300,
            "interval": 1,
        }
        mock_post.return_value = mock_response

        result: Auth0DeviceCodeAuthenticationDTO = command.execute()

        mock_post.assert_called_once()
        assert isinstance(result, Auth0DeviceCodeAuthenticationDTO)
        assert result.device_code == "test_device_code"

    def test_execute_http_error(self, mock_post: MagicMock):
        request_dto = Auth0FetchDeviceCodeRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            audience="test_audience",
            scope=["openid", "profile", "email"],
            algorithms=["RS256"],
        )
        command: Auth0FetchDeviceCodeCommand = Auth0FetchDeviceCodeCommand(request_dto)

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "some_error",
            "error_description": "some_description",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(Auth0APIError) as excinfo:
            command.execute()

        assert excinfo.value.error == "some_error"
        assert excinfo.value.status_code == 400
        assert excinfo.value.error_description == "some_description"


@patch("exalsius.core.commons.commands.requests.post")
@patch("exalsius.auth.commands.sleep")
@patch("exalsius.auth.commands.time")
class TestAuth0PollForAuthenticationCommand:
    def test_execute_success_on_first_try(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 2.0, 3.0]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        result: Auth0AuthenticationDTO = command.execute()

        assert isinstance(result, Auth0AuthenticationDTO)
        assert result.access_token == "test_access_token"

    def test_execute_success_after_retries_with_slow_down_error(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3, 1.4]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=2,
            poll_interval_seconds=1,
            poll_timeout_seconds=1,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response_slow_down = MagicMock()
        mock_response_slow_down.headers = {"Content-Type": "application/json"}
        mock_response_slow_down.status_code = 429
        mock_response_slow_down.json.return_value = {
            "error": "slow_down",
            "error_description": "slow down",
        }
        http_error_slow_down = requests.HTTPError(response=mock_response_slow_down)
        mock_response_slow_down.raise_for_status.side_effect = http_error_slow_down

        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        mock_post.side_effect = [mock_response_slow_down, mock_response]

        result: Auth0AuthenticationDTO = command.execute()
        assert result.access_token == "test_access_token"
        assert mock_post.call_count == 2

    def test_execute_fails_after_retries_with_user_abort_error(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=3,
            poll_interval_seconds=1,
            poll_timeout_seconds=1,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": "user abort error",
            "error_description": "user aborted the authentication process",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(Auth0AuthenticationError) as excinfo:
            command.execute()
        assert (
            excinfo.value.message
            == "failed to login. reason: user aborted the authentication process"
        )
        assert mock_post.call_count == 1

    def test_execute_fails_after_retries_with_unknown_error(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=3,
            poll_interval_seconds=1,
            poll_timeout_seconds=1,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": "unknown error",
            "error_description": "unknown error",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = [
            http_error,
            http_error,
            http_error,
        ]
        mock_post.return_value = mock_response

        with pytest.raises(Auth0AuthenticationError):
            command.execute()
        assert mock_post.call_count == 3

    def test_execute_fails_with_timeout_error(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 3.0]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=3,
            poll_interval_seconds=1,
            poll_timeout_seconds=1,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": "authorization_pending",
            "error_description": "authorization pending",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(TimeoutError):
            command.execute()
        assert mock_post.call_count == 0

    def test_execute_success_after_authorization_pending(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response_pending = MagicMock()
        mock_response_pending.headers = {"Content-Type": "application/json"}
        mock_response_pending.status_code = 403
        mock_response_pending.json.return_value = {
            "error": "authorization_pending",
            "error_description": "authorization pending",
        }
        http_error_pending = requests.HTTPError(response=mock_response_pending)
        mock_response_pending.raise_for_status.side_effect = http_error_pending

        mock_response_success = MagicMock()
        mock_response_success.headers = {"Content-Type": "application/json"}
        mock_response_success.json.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        mock_post.side_effect = [mock_response_pending, mock_response_success]

        result: Auth0AuthenticationDTO = command.execute()
        assert result.access_token == "test_access_token"
        assert mock_post.call_count == 2

    def test_execute_fails_with_empty_access_token(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=2,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "access_token": "",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        with pytest.raises(Auth0AuthenticationError) as excinfo:
            command.execute()
        assert "auth0 returned an empty access token" in excinfo.value.message
        assert mock_post.call_count == 2

    def test_execute_retries_on_generic_exception(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]

        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=2,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response_success = MagicMock()
        mock_response_success.headers = {"Content-Type": "application/json"}
        mock_response_success.json.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        mock_post.side_effect = [Exception("some generic error"), mock_response_success]

        result: Auth0AuthenticationDTO = command.execute()
        assert result.access_token == "test_access_token"
        assert mock_post.call_count == 2

    def test_execute_retries_on_403_without_error_key(
        self, mock_time: MagicMock, mock_sleep: MagicMock, mock_post: MagicMock
    ):
        mock_time.side_effect = [1.0, 1.1, 1.2, 1.3]
        request_dto = Auth0PollForAuthenticationRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            device_code="test_device_code",
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            retry_limit=2,
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request_dto
        )

        mock_sleep.return_value = None
        mock_response_403 = MagicMock()
        mock_response_403.status_code = 403
        mock_response_403.headers = {"Content-Type": "application/json"}
        mock_response_403.json.return_value = {"message": "Forbidden"}
        http_error_403 = requests.HTTPError(response=mock_response_403)
        mock_response_403.raise_for_status.side_effect = http_error_403

        mock_response_success = MagicMock()
        mock_response_success.headers = {"Content-Type": "application/json"}
        mock_response_success.json.return_value = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "scope": "openid",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        mock_post.side_effect = [mock_response_403, mock_response_success]

        result: Auth0AuthenticationDTO = command.execute()
        assert result.access_token == "test_access_token"
        assert mock_post.call_count == 2


@patch("exalsius.auth.commands.TokenVerifier")
@patch("exalsius.auth.commands.AsymmetricSignatureVerifier")
class TestAuth0ValidateTokenCommand:
    def test_execute_success(
        self, mock_signature_verifier: MagicMock, mock_token_verifier: MagicMock
    ):
        request_dto = Auth0ValidateTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            id_token="test_id_token",
        )
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(request_dto)
        mock_tv_instance = mock_token_verifier.return_value
        mock_tv_instance.verify.return_value = {
            "email": "test@exalsius.com",
            "sub": "123",
        }

        result: Auth0UserInfoDTO = command.execute()

        assert isinstance(result, Auth0UserInfoDTO)
        assert result.email == "test@exalsius.com"

    def test_execute_token_validation_error(
        self, mock_signature_verifier: MagicMock, mock_token_verifier: MagicMock
    ):
        request_dto = Auth0ValidateTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            id_token="test_id_token",
        )
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(request_dto)
        mock_tv_instance = mock_token_verifier.return_value
        mock_tv_instance.verify.side_effect = TokenValidationError("Invalid token")

        with pytest.raises(Auth0AuthenticationError) as excinfo:
            command.execute()
        assert "failed to validate token: Invalid token" in str(excinfo.value)

    def test_execute_generic_error(
        self, mock_signature_verifier: MagicMock, mock_token_verifier: MagicMock
    ):
        request_dto = Auth0ValidateTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            id_token="test_id_token",
        )
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(request_dto)
        mock_tv_instance = mock_token_verifier.return_value
        mock_tv_instance.verify.side_effect = Exception("Some generic error")

        with pytest.raises(Auth0AuthenticationError) as excinfo:
            command.execute()
        assert "unexpected error while validating token: Some generic error" in str(
            excinfo.value
        )


@patch("exalsius.auth.commands.keyring")
class TestStoreTokenOnKeyringCommand:
    def test_execute_success(self, mock_keyring: MagicMock):
        request = StoreTokenOnKeyringRequestDTO(
            client_id="test_client_id",
            access_token="test_token",
            expires_in=3600,
            refresh_token="test_refresh_token",
        )
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(request)
        result = command.execute()
        assert isinstance(result, TokenKeyringStorageStatusDTO)
        assert result.success is True
        assert mock_keyring.set_password.call_count == 3

    def test_execute_success_without_refresh_token(self, mock_keyring: MagicMock):
        request = StoreTokenOnKeyringRequestDTO(
            client_id="test_client_id",
            access_token="test_token",
            expires_in=3600,
            refresh_token=None,
        )
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(request)
        result = command.execute()
        assert isinstance(result, TokenKeyringStorageStatusDTO)
        assert result.success is True
        assert mock_keyring.set_password.call_count == 2

    def test_execute_keyring_error(self, mock_keyring: MagicMock):
        mock_keyring.set_password.side_effect = Exception("Keyring is locked")
        request = StoreTokenOnKeyringRequestDTO(
            client_id="test_client_id", access_token="test_token", expires_in=3600
        )
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(request)
        with pytest.raises(KeyringError):
            command.execute()


@patch("exalsius.auth.commands.keyring")
class TestLoadTokenFromKeyringCommand:
    def test_execute_success(self, mock_keyring: MagicMock):
        expiry_time = datetime.now() + timedelta(hours=1)
        mock_keyring.get_password.side_effect = [
            "test_access_token",
            expiry_time.isoformat(),
            "test_refresh_token",
        ]
        request: LoadTokenFromKeyringRequestDTO = LoadTokenFromKeyringRequestDTO(
            client_id="test_client_id"
        )
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(request)
        result: LoadedTokenDTO = command.execute()
        assert isinstance(result, LoadedTokenDTO)
        assert result.access_token == "test_access_token"
        assert result.expiry == expiry_time

    def test_token_not_found(self, mock_keyring: MagicMock):
        mock_keyring.get_password.return_value = None
        request: LoadTokenFromKeyringRequestDTO = LoadTokenFromKeyringRequestDTO(
            client_id="test_client_id",
        )
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(request)
        with pytest.raises(KeyringError):
            command.execute()

    def test_token_found_but_expiry_not(self, mock_keyring: MagicMock):
        mock_keyring.get_password.side_effect = ["test_access_token", None, None]
        request: LoadTokenFromKeyringRequestDTO = LoadTokenFromKeyringRequestDTO(
            client_id="test_client_id",
        )
        command = LoadTokenFromKeyringCommand(request)
        with pytest.raises(KeyringError):
            command.execute()

    def test_execute_keyring_exception(self, mock_keyring: MagicMock):
        mock_keyring.get_password.side_effect = Exception("Keyring is locked")
        request: LoadTokenFromKeyringRequestDTO = LoadTokenFromKeyringRequestDTO(
            client_id="test_client_id",
        )
        command = LoadTokenFromKeyringCommand(request)
        with pytest.raises(KeyringError):
            command.execute()


@patch("exalsius.core.commons.commands.requests.post")
class TestAuth0RefreshTokenCommand:
    def test_execute_success(self, mock_post: MagicMock):
        request = Auth0RefreshTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            refresh_token="test_refresh_token",
        )
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(request)
        mock_response: MagicMock = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "id_token": "new_id_token",
            "scope": "openid",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response
        result: Auth0AuthenticationDTO = command.execute()
        assert isinstance(result, Auth0AuthenticationDTO)
        assert result.access_token == "new_access_token"

    def test_execute_success_with_scope(self, mock_post: MagicMock):
        request = Auth0RefreshTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            refresh_token="test_refresh_token",
            scope=["openid", "profile", "node:agent"],
        )
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(request)
        mock_response: MagicMock = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "access_token": "new_access_token_with_scope",
            "id_token": "new_id_token",
            "scope": "openid profile node:agent",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        result: Auth0AuthenticationDTO = command.execute()

        assert isinstance(result, Auth0AuthenticationDTO)
        assert result.access_token == "new_access_token_with_scope"
        assert result.scope == "openid profile node:agent"

        # Verify the scope was included in the payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "scope" in call_args[1]["data"]
        assert call_args[1]["data"]["scope"] == "openid profile node:agent"

    def test_execute_http_error_with_scope(self, mock_post: MagicMock):
        request = Auth0RefreshTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            refresh_token="test_refresh_token",
            scope=["invalid_scope"],
        )
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(request)

        mock_response: MagicMock = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": "server_error",
            "error_description": "Scope escalation not allowed",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError) as excinfo:
            command.execute()

        # Check the response attributes
        assert excinfo.value.response.status_code == 500
        assert excinfo.value.response.json()["error"] == "server_error"
        assert (
            "Scope escalation not allowed"
            in excinfo.value.response.json()["error_description"]
        )


@patch("exalsius.core.commons.commands.requests.post")
class TestAuth0RevokeTokenCommand:
    def test_execute_success(self, mock_post: MagicMock):
        request = Auth0RevokeTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            token="test_token_to_revoke",
            token_type_hint="access_token",
        )
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(request)
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        result: Auth0RevokeTokenStatusDTO = command.execute()
        assert isinstance(result, Auth0RevokeTokenStatusDTO)
        assert result.success

    def test_execute_http_error(self, mock_post: MagicMock):
        request = Auth0RevokeTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            token="test_token_to_revoke",
            token_type_hint="access_token",
        )
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(request)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "some_error",
            "error_description": "some_description",
        }
        http_error = requests.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        with pytest.raises(Auth0APIError) as excinfo:
            command.execute()

        assert excinfo.value.error == "some_error"
        assert excinfo.value.status_code == 400
        assert excinfo.value.error_description == "some_description"

    def test_execute_generic_error(self, mock_post: MagicMock):
        request = Auth0RevokeTokenRequestDTO(
            domain="test.domain",
            client_id="test_client_id",
            token="test_token_to_revoke",
            token_type_hint="access_token",
        )
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(request)
        mock_post.side_effect = Exception("Some generic error")

        with pytest.raises(Auth0APIError) as excinfo:
            command.execute()
        assert excinfo.value.error == "unexpected error while revoking token"
        assert excinfo.value.status_code == 500
        assert str(excinfo.value.error_description) == "Some generic error"


@patch("exalsius.auth.commands.keyring")
class TestClearTokenFromKeyringCommand:
    def test_execute_success(self, mock_keyring: MagicMock):
        request: ClearTokenFromKeyringRequestDTO = ClearTokenFromKeyringRequestDTO(
            client_id="test_client_id",
        )
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(request)
        result: TokenKeyringStorageStatusDTO = command.execute()

        assert result.success is True
        assert mock_keyring.delete_password.call_count == 3
        mock_keyring.delete_password.assert_any_call(
            KeyringKeys.SERVICE_KEY,
            f"{request.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
        )

    def test_partial_success(self, mock_keyring: MagicMock):
        mock_keyring.delete_password.side_effect = [None, Exception("Error"), None]
        request: ClearTokenFromKeyringRequestDTO = ClearTokenFromKeyringRequestDTO(
            client_id="test_client_id",
        )
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(request)
        result: TokenKeyringStorageStatusDTO = command.execute()
        assert result.success is False

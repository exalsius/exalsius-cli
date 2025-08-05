from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from exalsius.auth.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0PollForAuthenticationCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exalsius.auth.models import (
    Auth0AuthenticationDTO,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0UserInfoDTO,
    LoadedTokenDTO,
    NotLoggedInWarning,
)
from exalsius.auth.service import Auth0Service
from exalsius.config import AppConfig, Auth0Config
from exalsius.core.commons.models import ServiceError


class TestAuth0Service:
    @pytest.fixture
    def mock_app_config(self):
        mock_auth0_config = MagicMock(spec=Auth0Config)
        mock_auth0_config.domain = "test.domain"
        mock_auth0_config.client_id = "test_client_id"
        mock_auth0_config.audience = "test_audience"
        mock_auth0_config.scope = ["test_scope"]
        mock_auth0_config.algorithms = ["RS256"]
        mock_auth0_config.device_code_grant_type = (
            "urn:ietf:params:oauth:grant-type:device_code"
        )
        mock_auth0_config.device_code_poll_interval_seconds = 5
        mock_auth0_config.device_code_poll_timeout_seconds = 120
        mock_auth0_config.device_code_retry_limit = 3
        mock_auth0_config.token_expiry_buffer_minutes = 5

        mock_app_config = MagicMock(spec=AppConfig)
        mock_app_config.auth0 = mock_auth0_config
        return mock_app_config

    @pytest.fixture
    def auth_service(self, mock_app_config):
        return Auth0Service(mock_app_config)

    def test_fetch_device_code(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")
        expected_dto = Auth0DeviceCodeAuthenticationDTO(
            device_code="test_code",
            user_code="test_user_code",
            verification_uri="https://test.uri",
            verification_uri_complete="https://test.uri/complete",
            expires_in=300,
            interval=5,
        )
        mock_execute.return_value = expected_dto

        result = auth_service.fetch_device_code()

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, Auth0FetchDeviceCodeCommand)
        assert result == expected_dto

    def test_poll_for_authentication(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")
        expected_dto = Auth0AuthenticationDTO(
            access_token="access_token",
            id_token="id_token",
            scope="scope",
            expires_in=3600,
            token_type="Bearer",
        )
        mock_execute.return_value = expected_dto

        result = auth_service.poll_for_authentication("test_device_code")

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, Auth0PollForAuthenticationCommand)
        assert command.request.device_code == "test_device_code"
        assert result == expected_dto

    def test_validate_token(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")
        expected_dto = Auth0UserInfoDTO(sub="user_id", email="test@test.com")
        mock_execute.return_value = expected_dto

        result = auth_service.validate_token("test_id_token")

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, Auth0ValidateTokenCommand)
        assert command.request.id_token == "test_id_token"
        assert result == expected_dto

    def test_store_token_on_keyring(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")

        auth_service.store_token_on_keyring("test_token", 3600, "test_refresh_token")

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, StoreTokenOnKeyringCommand)
        assert command.request.access_token == "test_token"

    def test_load_access_token_from_keyring(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")
        expected_dto = LoadedTokenDTO(
            access_token="test_token",
            expiry=datetime.now(),
            refresh_token="refresh_token",
        )
        mock_execute.return_value = expected_dto

        result = auth_service.load_access_token_from_keyring()

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, LoadTokenFromKeyringCommand)
        assert result == expected_dto

    def test_refresh_access_token(self, auth_service, mocker):
        mock_execute = mocker.patch.object(auth_service, "_execute_command")
        expected_dto = Auth0AuthenticationDTO(
            access_token="new_access_token",
            id_token="new_id_token",
            scope="scope",
            expires_in=3600,
            token_type="Bearer",
            refresh_token="new_refresh_token",
        )
        mock_execute.return_value = expected_dto

        result = auth_service.refresh_access_token("test_refresh_token")

        mock_execute.assert_called_once()
        command = mock_execute.call_args[0][0]
        assert isinstance(command, Auth0RefreshTokenCommand)
        assert command.request.refresh_token == "test_refresh_token"
        assert result == expected_dto

    def test_acquire_access_token_valid_token(self, auth_service, mocker):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_refresh = mocker.patch.object(auth_service, "refresh_access_token")

        future_expiry = datetime.now() + timedelta(minutes=10)
        loaded_token = LoadedTokenDTO(
            access_token="valid_token",
            expiry=future_expiry,
            refresh_token="refresh_token",
        )
        mock_load.return_value = loaded_token

        token = auth_service.acquire_access_token()

        assert token == "valid_token"
        mock_load.assert_called_once()
        mock_refresh.assert_not_called()

    def test_acquire_access_token_expired_token_refresh_success(
        self, auth_service, mocker
    ):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_refresh = mocker.patch.object(auth_service, "refresh_access_token")
        mock_store = mocker.patch.object(auth_service, "store_token_on_keyring")

        past_expiry = datetime.now() - timedelta(minutes=1)
        loaded_token = LoadedTokenDTO(
            access_token="expired_token",
            expiry=past_expiry,
            refresh_token="refresh_token",
        )
        mock_load.return_value = loaded_token

        refreshed_auth_dto = Auth0AuthenticationDTO(
            access_token="new_access_token",
            id_token="new_id_token",
            scope="openid profile",
            expires_in=3600,
            token_type="Bearer",
            refresh_token="new_refresh_token",
        )
        mock_refresh.return_value = refreshed_auth_dto

        token = auth_service.acquire_access_token()

        assert token == "new_access_token"
        mock_load.assert_called_once()
        mock_refresh.assert_called_once_with("refresh_token")
        mock_store.assert_called_once_with(
            token="new_access_token",
            expires_in=3600,
            refresh_token="new_refresh_token",
        )

    def test_acquire_access_token_expired_token_no_refresh_token(
        self, auth_service, mocker
    ):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")

        past_expiry = datetime.now() - timedelta(minutes=1)
        loaded_token = LoadedTokenDTO(
            access_token="expired_token", expiry=past_expiry, refresh_token=None
        )
        mock_load.return_value = loaded_token

        with pytest.raises(
            ServiceError, match="Session is expired. Please log in again."
        ):
            auth_service.acquire_access_token()

    def test_acquire_access_token_expired_token_refresh_fails(
        self, auth_service, mocker
    ):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_refresh = mocker.patch.object(auth_service, "refresh_access_token")

        past_expiry = datetime.now() - timedelta(minutes=1)
        loaded_token = LoadedTokenDTO(
            access_token="expired_token",
            expiry=past_expiry,
            refresh_token="refresh_token",
        )
        mock_load.return_value = loaded_token
        mock_refresh.side_effect = ServiceError("Refresh failed")

        with pytest.raises(
            ServiceError,
            match="failed to refresh access token: Refresh failed. Please log in again.",
        ):
            auth_service.acquire_access_token()

    def test_acquire_access_token_load_fails(self, auth_service, mocker):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_load.side_effect = ServiceError("Could not load from keyring")

        with pytest.raises(
            ServiceError, match="You are not logged in. Please log in first."
        ):
            auth_service.acquire_access_token()

    def test_logout_success(self, auth_service, mocker):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_execute = mocker.patch.object(auth_service, "_execute_command")

        loaded_token = LoadedTokenDTO(
            access_token="test_token",
            expiry=datetime.now() + timedelta(days=1),
            refresh_token="refresh_token",
        )
        mock_load.return_value = loaded_token

        auth_service.logout()

        mock_load.assert_called_once()
        assert mock_execute.call_count == 2
        revoke_command = mock_execute.call_args_list[0][0][0]
        clear_command = mock_execute.call_args_list[1][0][0]
        assert isinstance(revoke_command, Auth0RevokeTokenCommand)
        assert revoke_command.request.token == "test_token"
        assert isinstance(clear_command, ClearTokenFromKeyringCommand)

    def test_logout_not_logged_in(self, auth_service, mocker):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_load.side_effect = ServiceError("Not logged in")

        with pytest.raises(NotLoggedInWarning, match="You are not logged in."):
            auth_service.logout()

    def test_logout_revoke_fails(self, auth_service, mocker):
        mock_load = mocker.patch.object(auth_service, "load_access_token_from_keyring")
        mock_execute = mocker.patch.object(auth_service, "_execute_command")

        loaded_token = LoadedTokenDTO(
            access_token="test_token",
            expiry=datetime.now() + timedelta(days=1),
            refresh_token="refresh_token",
        )
        mock_load.return_value = loaded_token

        mock_execute.side_effect = [ServiceError("Revoke failed"), None]

        auth_service.logout()

        assert mock_execute.call_count == 2
        clear_command = mock_execute.call_args_list[1][0][0]
        assert isinstance(clear_command, ClearTokenFromKeyringCommand)

    def test_open_browser_for_device_code_authentication_silent(
        self, auth_service, mocker
    ):
        mocker.patch(
            "exalsius.auth.service._register_silent_browser", return_value=True
        )
        mock_open_browser = mocker.patch.object(
            auth_service, "_Auth0Service__open_browser"
        )
        mock_webbrowser_get = mocker.patch("webbrowser.get")

        auth_service.open_browser_for_device_code_authentication("http://test.com")

        mock_webbrowser_get.assert_called_once_with("silent")
        mock_open_browser.assert_called_once_with(
            mock_webbrowser_get.return_value, "http://test.com"
        )

    def test_open_browser_for_device_code_authentication_default(
        self, auth_service, mocker
    ):
        mocker.patch(
            "exalsius.auth.service._register_silent_browser", return_value=False
        )
        mock_open_browser = mocker.patch.object(
            auth_service, "_Auth0Service__open_browser"
        )
        mock_webbrowser_get = mocker.patch("webbrowser.get")

        auth_service.open_browser_for_device_code_authentication("http://test.com")

        mock_webbrowser_get.assert_called_once_with()
        mock_open_browser.assert_called_once_with(
            mock_webbrowser_get.return_value, "http://test.com"
        )

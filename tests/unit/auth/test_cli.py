from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from exalsius.app import app
from exalsius.auth.models import (
    Auth0AuthenticationDTO,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0UserInfoDTO,
    NotLoggedInWarning,
)
from exalsius.core.commons.models import ServiceError, ServiceWarning


@pytest.fixture
def runner():
    return CliRunner()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_success_interactive(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.return_value = (
        Auth0DeviceCodeAuthenticationDTO(
            device_code="test_device_code",
            user_code="test_user_code",
            verification_uri="https://test.com",
            verification_uri_complete="https://test.com/complete",
            expires_in=300,
            interval=5,
        )
    )
    mock_auth_service_instance.poll_for_authentication.return_value = (
        Auth0AuthenticationDTO(
            access_token="test_access_token",
            id_token="test_id_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
            scope="test",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )

    with patch("exalsius.auth.cli.utils.is_interactive", return_value=True):
        mock_auth_service_instance.open_browser_for_device_code_authentication.return_value = (
            True
        )
        result = runner.invoke(app, ["login"])

    assert result.exit_code == 0
    mock_auth_service_instance.fetch_device_code.assert_called_once()
    mock_display_manager_instance.display_device_code_polling_started_via_browser.assert_called_once()
    mock_auth_service_instance.poll_for_authentication.assert_called_once_with(
        "test_device_code"
    )
    mock_auth_service_instance.validate_token.assert_called_once_with("test_id_token")
    mock_auth_service_instance.store_token_on_keyring.assert_called_once()
    mock_display_manager_instance.display_authentication_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_success_non_interactive(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.return_value = (
        Auth0DeviceCodeAuthenticationDTO(
            device_code="test_device_code",
            user_code="test_user_code",
            verification_uri="https://test.com",
            verification_uri_complete="https://test.com/complete",
            expires_in=300,
            interval=5,
        )
    )
    mock_auth_service_instance.poll_for_authentication.return_value = (
        Auth0AuthenticationDTO(
            access_token="test_access_token",
            id_token="test_id_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
            scope="test",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )

    with patch("exalsius.auth.cli.utils.is_interactive", return_value=False):
        result = runner.invoke(app, ["login"])

    assert result.exit_code == 0
    mock_display_manager_instance.display_device_code_polling_started.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_fetch_device_code_error(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.side_effect = ServiceError(
        "Failed to fetch device code"
    )

    result = runner.invoke(app, ["login"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Failed to fetch device code"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_polling_cancelled(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.return_value = (
        Auth0DeviceCodeAuthenticationDTO(
            device_code="test_device_code",
            user_code="test_user_code",
            verification_uri="https://test.com",
            verification_uri_complete="https://test.com/complete",
            expires_in=300,
            interval=5,
        )
    )
    mock_auth_service_instance.poll_for_authentication.side_effect = KeyboardInterrupt

    result = runner.invoke(app, ["login"])

    assert result.exit_code == 0
    mock_display_manager_instance.display_device_code_polling_cancelled.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_validate_token_error(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.return_value = (
        Auth0DeviceCodeAuthenticationDTO(
            device_code="test_device_code",
            user_code="test_user_code",
            verification_uri="https://test.com",
            verification_uri_complete="https://test.com/complete",
            expires_in=300,
            interval=5,
        )
    )
    mock_auth_service_instance.poll_for_authentication.return_value = (
        Auth0AuthenticationDTO(
            access_token="test_access_token",
            id_token="test_id_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
            scope="test",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.side_effect = ServiceError(
        "Token validation failed"
    )

    result = runner.invoke(app, ["login"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Token validation failed"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_store_token_error(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.return_value = (
        Auth0DeviceCodeAuthenticationDTO(
            device_code="test_device_code",
            user_code="test_user_code",
            verification_uri="https://test.com",
            verification_uri_complete="https://test.com/complete",
            expires_in=300,
            interval=5,
        )
    )
    mock_auth_service_instance.poll_for_authentication.return_value = (
        Auth0AuthenticationDTO(
            access_token="test_access_token",
            id_token="test_id_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
            scope="test",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )
    mock_auth_service_instance.store_token_on_keyring.side_effect = ServiceError(
        "Failed to store token"
    )

    result = runner.invoke(app, ["login"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Failed to store token"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_logout_success(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 0
    mock_auth_service_instance.logout.assert_called_once()
    mock_display_manager_instance.display_logout_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_logout_not_logged_in(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.logout.side_effect = NotLoggedInWarning(
        "You are not logged in."
    )

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 0
    mock_display_manager_instance.display_not_logged_in.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_logout_service_warning(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.logout.side_effect = ServiceWarning(
        "Could not revoke token"
    )

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 0
    mock_display_manager_instance.display_logout_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_logout_service_error(
    mock_auth0_service, mock_display_manager, mock_get_app_state, runner
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.logout.side_effect = ServiceError("Failed to logout")

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Failed to logout"
    )

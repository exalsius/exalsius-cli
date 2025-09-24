from typing import Any
from unittest.mock import MagicMock, patch

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


def print_cli_runner_result_details(result: Any):
    """
    Print detailed information about a FastAPI TestClient response.

    Args:
        result: The response object from FastAPI's TestClient
    """
    print("\n=== Result Details ===")
    for name in dir(result):
        if name.startswith("_"):  # skip dunder/private
            continue
        try:
            value: Any = getattr(result, name)
        except Exception as e:
            print(f"{name}: <error {type(e).__name__}> {e}")
        else:
            print(f"{name}: {value!r}")
    print("=====================\n")


@pytest.fixture
def runner():
    return CliRunner()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_success_interactive(
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
def test_login_interactive_browser_open_fails(
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
            False
        )
        result = runner.invoke(app, ["login"])

    assert result.exit_code == 0
    mock_auth_service_instance.fetch_device_code.assert_called_once()
    mock_display_manager_instance.display_device_code_polling_started.assert_called_once()
    mock_display_manager_instance.display_device_code_polling_started_via_browser.assert_not_called()
    mock_auth_service_instance.poll_for_authentication.assert_called_once_with(
        "test_device_code"
    )
    mock_auth_service_instance.validate_token.assert_called_once_with("test_id_token")
    mock_auth_service_instance.store_token_on_keyring.assert_called_once()
    mock_display_manager_instance.display_authentication_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
def test_login_fetch_device_code_error(
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
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
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.logout.side_effect = ServiceError("Failed to logout")

    result = runner.invoke(app, ["logout"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Failed to logout"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_success_interactive(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    # Setup mock app state
    mock_original_app_state = MagicMock()
    mock_original_app_state.config.auth0.scope = ["openid", "profile", "email"]
    mock_original_app_state.config.auth0_node_agent.client_id = "node_agent_client_id"
    mock_original_app_state.config.auth0_node_agent.scope = [
        "openid",
        "profile",
        "node:agent",
    ]
    mock_get_app_state.return_value = mock_original_app_state

    mock_modified_app_state = MagicMock()
    mock_deepcopy.return_value = mock_modified_app_state

    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    # Mock the authorization workflow responses
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
            access_token="test_node_agent_access_token",
            id_token="test_id_token",
            refresh_token="test_node_agent_refresh_token",
            expires_in=3600,
            scope="openid profile node:agent",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )

    # Mock scope_escalation_check to return successfully, because assertion exit code might irritate CI workflow
    mock_auth_service_instance.scope_escalation_check.return_value = None

    with patch("exalsius.auth.cli.utils.is_interactive", return_value=True):
        mock_auth_service_instance.open_browser_for_device_code_authentication.return_value = (
            True
        )
        result: Any = runner.invoke(app, ["deployment-token", "get"])

    if result.exit_code != 0:
        print_cli_runner_result_details(result)

    assert result.exit_code == 0
    mock_auth_service_instance.fetch_device_code.assert_called_once()
    mock_display_manager_instance.display_device_code_polling_started_via_browser.assert_called_once()
    mock_auth_service_instance.poll_for_authentication.assert_called_once_with(
        "test_device_code"
    )
    mock_auth_service_instance.validate_token.assert_called_once_with("test_id_token")
    mock_auth_service_instance.scope_escalation_check.assert_called_once_with(
        refresh_token="test_node_agent_refresh_token",
        current_scope=["openid", "profile", "node:agent"],
        reference_scope=["openid", "profile", "email"],
    )
    mock_display_manager_instance.display_deployment_token_request_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_fetch_device_code_error(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_original_app_state: MagicMock = MagicMock()
    mock_get_app_state.return_value = mock_original_app_state
    mock_deepcopy.return_value = MagicMock()

    mock_auth_service_instance = mock_auth0_service.return_value
    mock_display_manager_instance = mock_display_manager.return_value

    mock_auth_service_instance.fetch_device_code.side_effect = ServiceError(
        "Failed to fetch device code for node agent"
    )

    result: Any = runner.invoke(app, ["deployment-token", "get"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Failed to fetch device code for node agent"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_success_non_interactive(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_original_app_state: MagicMock = MagicMock()
    mock_original_app_state.config.auth0.scope = ["openid", "profile", "email"]
    mock_original_app_state.config.auth0_node_agent.client_id = "node_agent_client_id"
    mock_original_app_state.config.auth0_node_agent.scope = [
        "openid",
        "profile",
        "node:agent",
    ]
    mock_get_app_state.return_value = mock_original_app_state
    mock_modified_app_state: MagicMock = MagicMock()
    mock_deepcopy.return_value = mock_modified_app_state
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
            access_token="test_node_agent_access_token",
            id_token="test_id_token",
            refresh_token="test_node_agent_refresh_token",
            expires_in=3600,
            scope="openid profile node:agent",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )
    mock_auth_service_instance.scope_escalation_check.return_value = None

    with patch("exalsius.auth.cli.utils.is_interactive", return_value=False):
        result: Any = runner.invoke(app, ["deployment-token", "get"])

    if result.exit_code != 0:
        print_cli_runner_result_details(result)

    assert result.exit_code == 0
    mock_display_manager_instance.display_device_code_polling_started.assert_called_once()
    mock_display_manager_instance.display_deployment_token_request_success.assert_called_once()


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_scope_escalation_test_fails(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_original_app_state: MagicMock = MagicMock()
    mock_original_app_state.config.auth0.scope = ["openid", "profile", "email"]
    mock_original_app_state.config.auth0_node_agent.scope = [
        "openid",
        "profile",
        "node:agent",
    ]
    mock_get_app_state.return_value = mock_original_app_state
    mock_deepcopy.return_value = MagicMock()

    mock_auth_service_instance = mock_auth0_service.return_value

    # Mock successful authorization workflow
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
            access_token="test_node_agent_access_token",
            id_token="test_id_token",
            refresh_token="test_node_agent_refresh_token",
            expires_in=3600,
            scope="openid profile node:agent",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.return_value = Auth0UserInfoDTO(
        sub="test_sub",
        email="test@exalsius.com",
    )

    # Mock scope escalation test failure
    mock_auth_service_instance.scope_escalation_check.side_effect = AssertionError(
        "Scope escalation test failed"
    )

    result: Any = runner.invoke(app, ["deployment-token", "get"])

    # Should still exit with 1 due to the assertion error
    assert result.exit_code == 1


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_validate_token_error(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_original_app_state: MagicMock = MagicMock()
    mock_get_app_state.return_value = mock_original_app_state
    mock_deepcopy.return_value = MagicMock()

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
            access_token="test_node_agent_access_token",
            id_token="test_id_token",
            refresh_token="test_node_agent_refresh_token",
            expires_in=3600,
            scope="openid profile node:agent",
            token_type="Bearer",
        )
    )
    mock_auth_service_instance.validate_token.side_effect = ServiceError(
        "Token validation failed"
    )

    result: Any = runner.invoke(app, ["deployment-token", "get"])

    assert result.exit_code == 1
    mock_display_manager_instance.display_authentication_error.assert_called_once_with(
        "Token validation failed"
    )


@patch("exalsius.auth.cli.utils.get_app_state_from_ctx")
@patch("exalsius.auth.cli.AuthDisplayManager")
@patch("exalsius.auth.cli.Auth0Service")
@patch("exalsius.auth.cli.copy.deepcopy")
def test_get_deployment_token_polling_cancelled(
    mock_deepcopy: MagicMock,
    mock_auth0_service: MagicMock,
    mock_display_manager: MagicMock,
    mock_get_app_state: MagicMock,
    runner: CliRunner,
):
    mock_original_app_state: MagicMock = MagicMock()
    mock_get_app_state.return_value = mock_original_app_state
    mock_deepcopy.return_value = MagicMock()

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

    result: Any = runner.invoke(app, ["deployment-token", "get"])

    if result.exit_code != 0:
        print_cli_runner_result_details(result)

    assert result.exit_code == 0
    mock_display_manager_instance.display_device_code_polling_cancelled.assert_called_once()

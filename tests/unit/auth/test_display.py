from unittest.mock import MagicMock, patch

import pytest

from exalsius.auth.display import AuthDisplayManager


@pytest.fixture
def mock_console():
    return MagicMock()


@pytest.fixture
def display_manager(mock_console):
    return AuthDisplayManager(mock_console)


def test_display_device_code_polling_started(display_manager, mock_console):
    verification_uri_complete = "https://example.com/verify?code=123"
    user_code = "ABCD-EFGH"

    with patch("qrcode.QRCode") as mock_qr_code_class:
        mock_qr_instance = MagicMock()
        mock_qr_code_class.return_value = mock_qr_instance

        display_manager.display_device_code_polling_started(
            verification_uri_complete, user_code
        )

        assert mock_console.print.call_count > 5
        mock_console.print.assert_any_call(
            "[blue]Scan this QR code with your smartphone to complete login:[/blue]"
        )
        mock_qr_instance.print_ascii.assert_called_once_with(invert=True)
        mock_console.print.assert_any_call(f"[blue]{verification_uri_complete}[/blue]")
        mock_console.print.assert_any_call(f"[blue]{user_code}[/blue]")


def test_display_device_code_polling_started_via_browser(display_manager, mock_console):
    verification_uri_complete = "https://example.com/verify?code=123"
    user_code = "ABCD-EFGH"

    display_manager.display_device_code_polling_started_via_browser(
        verification_uri_complete, user_code
    )

    assert mock_console.print.call_count > 4
    mock_console.print.assert_any_call(
        "[blue]Your browser should have been opened.[/blue]"
    )
    mock_console.print.assert_any_call(f"[blue]{verification_uri_complete}[/blue]")
    mock_console.print.assert_any_call(f"[blue]{user_code}[/blue]")


def test_display_device_code_polling_cancelled(display_manager, mock_console):
    display_manager.display_device_code_polling_cancelled()
    mock_console.print.assert_called_once_with("[blue]Login canceled via Ctrl+C[/blue]")


def test_display_authentication_error(display_manager, mock_console):
    error_message = "Invalid credentials"
    display_manager.display_authentication_error(error_message)
    mock_console.print.assert_called_once_with(
        f"[red]Login error: {error_message}[/red]"
    )


def test_display_authentication_success_with_email(display_manager, mock_console):
    email = "test@example.com"
    sub = "subject"
    display_manager.display_authentication_success(email, sub)
    mock_console.print.assert_any_call(
        f"[green]You are successfully logged in as '{email}'[/green]"
    )
    mock_console.print.assert_any_call(
        "[green]Let's start setting up your workspaces![/green]"
    )


def test_display_authentication_success_with_sub(display_manager, mock_console):
    email = None
    sub = "subject"
    display_manager.display_authentication_success(email, sub)
    mock_console.print.assert_any_call(
        f"[green]You are successfully logged in as '{sub}'[/green]"
    )
    mock_console.print.assert_any_call(
        "[green]Let's start setting up your workspaces![/green]"
    )


def test_display_authentication_success_with_none(display_manager, mock_console):
    email = None
    sub = None
    display_manager.display_authentication_success(email, sub)
    mock_console.print.assert_any_call(
        "[green]You are successfully logged in as 'unknown'[/green]"
    )
    mock_console.print.assert_any_call(
        "[green]Let's start setting up your workspaces![/green]"
    )


def test_display_logout_success(display_manager, mock_console):
    display_manager.display_logout_success()
    mock_console.print.assert_called_once_with(
        "[green]Logged out successfully.[/green]"
    )


def test_display_not_logged_in(display_manager, mock_console):
    display_manager.display_not_logged_in()
    mock_console.print.assert_called_once_with("[blue]You are not logged in.[/blue]")


def test_display_node_agent_tokens_request_success_with_refresh_token(
    display_manager, mock_console
):
    access_token = "test_access_token_12345"
    refresh_token = "test_refresh_token_67890"
    expires_in = 3600
    scope = "openid profile node:agent"

    display_manager.display_node_agent_tokens_request_success(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        scope=scope,
    )

    # Verify the success message
    mock_console.print.assert_any_call(
        "[green]Requesting node agent tokens successful![/green]"
    )

    # Verify access token display
    mock_console.print.assert_any_call("[blue]New Access Token:[/blue]")
    mock_console.print.assert_any_call(f"[blue]{access_token}[/blue]")

    # Verify refresh token display
    mock_console.print.assert_any_call("[blue]New Refresh Token:[/blue]")
    mock_console.print.assert_any_call(f"[blue]{refresh_token}[/blue]")

    # Verify expires in display
    mock_console.print.assert_any_call(f"[blue]Expires in: {expires_in} seconds[/blue]")

    # Verify scope display
    mock_console.print.assert_any_call(f"[blue]Scope: {scope}[/blue]")

    # Verify warning about not storing tokens
    mock_console.print.assert_any_call(
        "[blue]Note: These tokens are not stored in the keyring.[/blue]"
    )


def test_display_node_agent_tokens_request_success_without_refresh_token(
    display_manager, mock_console
):
    access_token = "test_access_token_12345"
    expires_in = 3600
    scope = "openid profile node:agent"

    display_manager.display_node_agent_tokens_request_success(
        access_token=access_token,
        refresh_token=None,
        expires_in=expires_in,
        scope=scope,
    )

    # Verify the success message
    mock_console.print.assert_any_call(
        "[green]Requesting node agent tokens successful![/green]"
    )

    # Verify access token display
    mock_console.print.assert_any_call("[blue]New Access Token:[/blue]")
    mock_console.print.assert_any_call(f"[blue]{access_token}[/blue]")

    # Verify refresh token is NOT displayed
    assert not any(
        call
        for call in mock_console.print.call_args_list
        if "[blue]New Refresh Token:[/blue]" in str(call)
    )

    # Verify expires in display
    mock_console.print.assert_any_call(f"[blue]Expires in: {expires_in} seconds[/blue]")

    # Verify scope display
    mock_console.print.assert_any_call(f"[blue]Scope: {scope}[/blue]")

    # Verify warning about not storing tokens
    mock_console.print.assert_any_call(
        "[blue]Note: These tokens are not stored in the keyring.[/blue]"
    )

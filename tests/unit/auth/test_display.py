from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from exalsius.auth.display import AuthDisplayManager


def _get_printed_output(mock_console: MagicMock) -> str:
    """Helper to get all printed text from a mock console."""
    output: list[str] = []
    for call_args in mock_console.print.call_args_list:
        if call_args.args:
            output.append(str(call_args.args[0]))
    return "\\n".join(output)


@pytest.fixture
def mock_console() -> MagicMock:
    return MagicMock(spec=Console)


def test_display_device_code_polling_started(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.info_display.console = mock_console

    verification_uri_complete = "https://example.com/verify?code=123"
    user_code = "ABCD-EFGH"

    with patch("qrcode.QRCode") as mock_qr_code_class:
        mock_qr_instance = MagicMock()
        mock_qr_code_class.return_value = mock_qr_instance

        display_manager.display_device_code_polling_started(
            verification_uri_complete, user_code
        )

        printed_output = _get_printed_output(mock_console)

        assert (
            "Scan this QR code with your smartphone to complete login:"
            in printed_output
        )
        mock_qr_instance.print_ascii.assert_called_once_with(invert=True)
        assert verification_uri_complete in printed_output
        assert user_code in printed_output


def test_display_device_code_polling_started_via_browser(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.info_display.console = mock_console
    verification_uri_complete = "https://example.com/verify?code=123"
    user_code = "ABCD-EFGH"

    display_manager.display_device_code_polling_started_via_browser(
        verification_uri_complete, user_code
    )

    printed_output = _get_printed_output(mock_console)
    assert "Your browser should have been opened." in printed_output
    assert verification_uri_complete in printed_output
    assert user_code in printed_output


def test_display_device_code_polling_cancelled(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.info_display.console = mock_console
    display_manager.display_device_code_polling_cancelled()

    printed_output = _get_printed_output(mock_console)
    assert "Login canceled via Ctrl+C" in printed_output


def test_display_authentication_error(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.error_display.console = mock_console
    error_message = "Invalid credentials"
    display_manager.display_authentication_error(error_message)

    printed_output = _get_printed_output(mock_console)
    assert f"Login error: {error_message}" in printed_output


def test_display_authentication_success_with_email(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.success_display.console = mock_console
    email = "test@example.com"
    sub = "subject"
    display_manager.display_authentication_success(email, sub)

    printed_output = _get_printed_output(mock_console)
    assert f"You are successfully logged in as '{email}'" in printed_output
    assert "Let's start setting up your workspaces!" in printed_output


def test_display_authentication_success_with_sub(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.success_display.console = mock_console
    email = None
    sub = "subject"
    display_manager.display_authentication_success(email, sub)

    printed_output = _get_printed_output(mock_console)
    assert f"You are successfully logged in as '{sub}'" in printed_output
    assert "Let's start setting up your workspaces!" in printed_output


def test_display_authentication_success_with_none(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.success_display.console = mock_console
    email = None
    sub = None
    display_manager.display_authentication_success(email, sub)

    printed_output = _get_printed_output(mock_console)
    assert "You are successfully logged in as 'unknown'" in printed_output
    assert "Let's start setting up your workspaces!" in printed_output


def test_display_logout_success(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.success_display.console = mock_console
    display_manager.display_logout_success()

    printed_output = _get_printed_output(mock_console)
    assert "Logged out successfully." in printed_output


def test_display_not_logged_in(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.info_display.console = mock_console
    display_manager.display_not_logged_in()

    printed_output = _get_printed_output(mock_console)
    assert "You are not logged in." in printed_output


def test_display_deployment_token_request_success(mock_console: MagicMock):
    display_manager = AuthDisplayManager()
    display_manager.info_display.console = mock_console
    display_manager.success_display.console = mock_console
    access_token = "test_access_token_12345"

    display_manager.display_deployment_token_request_success(
        access_token=access_token,
    )

    printed_output = _get_printed_output(mock_console)
    assert "Request for deployment token successful!" in printed_output
    assert "Your deployment token is:" in printed_output
    assert access_token in printed_output

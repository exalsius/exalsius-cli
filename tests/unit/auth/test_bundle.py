"""Unit tests for AuthBundle flow detection."""

from unittest.mock import patch

from exls.auth.adapters.bundle import AuthBundle
from exls.auth.core.domain import AuthFlowType


class TestDetectAuthFlow:
    def test_override_pkce(self):
        result = AuthBundle.detect_auth_flow(override=AuthFlowType.PKCE)
        assert result == AuthFlowType.PKCE

    def test_override_device_code(self):
        result = AuthBundle.detect_auth_flow(override=AuthFlowType.DEVICE_CODE)
        assert result == AuthFlowType.DEVICE_CODE

    def test_override_auto_does_not_short_circuit(self):
        """AUTO override should fall through to detection logic."""
        with (
            patch("exls.auth.adapters.bundle.sys") as mock_sys,
            patch("exls.auth.adapters.bundle.os"),
        ):
            mock_sys.stdout.isatty.return_value = False
            result = AuthBundle.detect_auth_flow(override=AuthFlowType.AUTO)
            assert result == AuthFlowType.DEVICE_CODE

    def test_non_interactive_returns_device_code(self):
        with patch("exls.auth.adapters.bundle.sys") as mock_sys:
            mock_sys.stdout.isatty.return_value = False
            result = AuthBundle.detect_auth_flow()
            assert result == AuthFlowType.DEVICE_CODE

    def test_linux_no_display_returns_device_code(self):
        with (
            patch("exls.auth.adapters.bundle.sys") as mock_sys,
            patch("exls.auth.adapters.bundle.os") as mock_os,
        ):
            mock_sys.stdout.isatty.return_value = True
            mock_sys.platform = "linux"
            mock_os.environ.get.return_value = None
            result = AuthBundle.detect_auth_flow()
            assert result == AuthFlowType.DEVICE_CODE

    def test_linux_with_display_checks_browser(self):
        with (
            patch("exls.auth.adapters.bundle.sys") as mock_sys,
            patch("exls.auth.adapters.bundle.os") as mock_os,
            patch("webbrowser.get") as mock_get,
        ):
            mock_sys.stdout.isatty.return_value = True
            mock_sys.platform = "linux"
            mock_os.environ.get.side_effect = (
                lambda key: (  # pyright: ignore[reportUnknownLambdaType]
                    "/tmp/.X11" if key == "DISPLAY" else None
                )
            )
            mock_get.return_value = object()
            result = AuthBundle.detect_auth_flow()
            assert result == AuthFlowType.PKCE

    def test_linux_with_wayland_display_checks_browser(self):
        with (
            patch("exls.auth.adapters.bundle.sys") as mock_sys,
            patch("exls.auth.adapters.bundle.os") as mock_os,
            patch("webbrowser.get") as mock_get,
        ):
            mock_sys.stdout.isatty.return_value = True
            mock_sys.platform = "linux"
            mock_os.environ.get.side_effect = lambda key: (  # type: ignore[no-untyped-def]
                "wayland-0" if key == "WAYLAND_DISPLAY" else None
            )
            mock_get.return_value = object()
            result = AuthBundle.detect_auth_flow()
            assert result == AuthFlowType.PKCE

    def test_no_browser_returns_device_code(self):
        import webbrowser

        with (
            patch("exls.auth.adapters.bundle.sys") as mock_sys,
            patch("webbrowser.get", side_effect=webbrowser.Error("no browser")),
        ):
            mock_sys.stdout.isatty.return_value = True
            mock_sys.platform = "darwin"
            result = AuthBundle.detect_auth_flow()
            assert result == AuthFlowType.DEVICE_CODE

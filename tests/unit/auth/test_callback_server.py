"""Unit tests for OAuth callback server."""

import socket
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from exls.auth.adapters.auth0.callback_server import (
    CallbackResult,
    OAuthCallbackServer,
)
from exls.auth.core.ports.operations import AuthError


def _find_free_port() -> int:
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestOAuthCallbackServer:
    def test_start_returns_port(self):
        port = _find_free_port()
        server = OAuthCallbackServer(ports=[port])
        actual_port = server.start()
        try:
            assert actual_port == port
        finally:
            server.shutdown()

    def test_port_fallback(self):
        """When primary port is busy, server falls back to next port."""
        port1 = _find_free_port()
        port2 = _find_free_port()

        # Occupy port1 with a raw socket
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind(("127.0.0.1", port1))
        blocker.listen(1)
        try:
            server = OAuthCallbackServer(ports=[port1, port2])
            actual_port = server.start()
            try:
                assert actual_port == port2
            finally:
                server.shutdown()
        finally:
            blocker.close()

    def test_all_ports_unavailable_raises(self):
        port1 = _find_free_port()
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind(("127.0.0.1", port1))
        blocker.listen(1)
        try:
            server = OAuthCallbackServer(ports=[port1])
            with pytest.raises(AuthError, match="All callback ports unavailable"):
                server.start()
        finally:
            blocker.close()

    def test_successful_callback(self):
        port = _find_free_port()
        server = OAuthCallbackServer(ports=[port])
        server.start()
        try:
            # Simulate callback from Auth0
            url = f"http://127.0.0.1:{port}/callback?code=test-code&state=test-state"
            urlopen(url, timeout=5)

            result = server.wait_for_callback(timeout=5)
            assert result.code == "test-code"
            assert result.state == "test-state"
            assert result.error is None
        finally:
            server.shutdown()

    def test_error_callback(self):
        port = _find_free_port()
        server = OAuthCallbackServer(ports=[port])
        server.start()
        try:
            url = (
                f"http://127.0.0.1:{port}/callback"
                "?error=access_denied&error_description=User+denied+access"
            )
            with pytest.raises(HTTPError, match="400"):
                urlopen(url, timeout=5)

            result = server.wait_for_callback(timeout=5)
            assert result.error == "access_denied"
            assert result.error_description == "User denied access"
            assert result.code is None
        finally:
            server.shutdown()

    def test_timeout_raises(self):
        port = _find_free_port()
        server = OAuthCallbackServer(ports=[port])
        server.start()
        try:
            with pytest.raises(AuthError, match="timed out"):
                server.wait_for_callback(timeout=1)
        finally:
            server.shutdown()

    def test_shutdown_is_idempotent(self):
        port = _find_free_port()
        server = OAuthCallbackServer(ports=[port])
        server.start()
        server.shutdown()
        # Second call should not raise
        server.shutdown()


class TestCallbackResult:
    def test_success_result(self):
        result = CallbackResult(code="abc", state="xyz")
        assert result.code == "abc"
        assert result.state == "xyz"
        assert result.error is None

    def test_error_result(self):
        result = CallbackResult(error="access_denied", error_description="denied")
        assert result.code is None
        assert result.error == "access_denied"

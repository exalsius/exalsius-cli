"""Unit tests for Auth0PkceAdapter."""

from unittest.mock import MagicMock

import pytest

from exls.auth.adapters.auth0.callback_server import CallbackResult
from exls.auth.adapters.auth0.config import Auth0Config
from exls.auth.adapters.auth0.pkce_adapter import Auth0PkceAdapter
from exls.auth.core.domain import PkceSession
from exls.auth.core.ports.operations import AuthError


@pytest.fixture
def config() -> Auth0Config:
    return Auth0Config(
        domain="test.auth0.com",
        client_id="test-client-id",
        audience="https://test-api",
        scope=["openid", "profile", "email"],
        pkce_callback_port=8999,
        pkce_code_verifier_length=64,
        pkce_code_challenge_method="S256",
        pkce_callback_timeout_seconds=300,
    )


@pytest.fixture
def adapter(config: Auth0Config) -> Auth0PkceAdapter:
    return Auth0PkceAdapter(config=config)


@pytest.fixture
def session() -> PkceSession:
    return PkceSession(
        code_verifier="a" * 64,
        state="test-state",
        nonce="test-nonce",
        redirect_uri="http://127.0.0.1:8999/callback",
    )


def _inject_mock_server(adapter: Auth0PkceAdapter, mock_server: MagicMock) -> None:
    """Helper to inject a mock server into the adapter for testing."""
    object.__setattr__(adapter, "_server", mock_server)


class TestGeneratePkceSession:
    def test_uses_provided_redirect_uri(self, adapter: Auth0PkceAdapter):
        session = adapter.generate_pkce_session("http://127.0.0.1:9001/callback")
        assert session.redirect_uri == "http://127.0.0.1:9001/callback"

    def test_generates_non_empty_fields(self, adapter: Auth0PkceAdapter):
        session = adapter.generate_pkce_session("http://127.0.0.1:8999/callback")
        assert len(session.code_verifier) == 64
        assert len(session.state) > 0
        assert len(session.nonce) > 0

    def test_sessions_are_unique(self, adapter: Auth0PkceAdapter):
        s1 = adapter.generate_pkce_session("http://127.0.0.1:8999/callback")
        s2 = adapter.generate_pkce_session("http://127.0.0.1:8999/callback")
        assert s1.code_verifier != s2.code_verifier
        assert s1.state != s2.state


class TestBuildAuthorizationUrl:
    def test_includes_required_params(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        url = adapter.build_authorization_url(session)
        assert "response_type=code" in url
        assert "client_id=test-client-id" in url
        assert "code_challenge=" in url
        assert "code_challenge_method=S256" in url
        assert "redirect_uri=" in url
        assert "state=test-state" in url
        assert "nonce=test-nonce" in url
        assert url.startswith("https://test.auth0.com/authorize?")

    def test_includes_organization_when_provided(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        url = adapter.build_authorization_url(session, organization="org_123")
        assert "organization=org_123" in url

    def test_excludes_organization_when_not_provided(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        url = adapter.build_authorization_url(session)
        assert "organization" not in url


class TestWaitForCallback:
    def test_raises_when_server_not_started(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        with pytest.raises(AuthError, match="Callback server not started"):
            adapter.wait_for_callback(session)

    def test_raises_on_error_result(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        mock_server = MagicMock()
        mock_server.wait_for_callback.return_value = CallbackResult(
            error="access_denied",
            error_description="User denied",
            state="test-state",
        )
        _inject_mock_server(adapter, mock_server)

        with pytest.raises(AuthError, match="Authentication failed"):
            adapter.wait_for_callback(session)

    def test_raises_on_state_mismatch(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        mock_server = MagicMock()
        mock_server.wait_for_callback.return_value = CallbackResult(
            code="auth-code",
            state="wrong-state",
        )
        _inject_mock_server(adapter, mock_server)

        with pytest.raises(AuthError, match="State mismatch"):
            adapter.wait_for_callback(session)

    def test_raises_on_missing_code(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        mock_server = MagicMock()
        mock_server.wait_for_callback.return_value = CallbackResult(
            code=None,
            state="test-state",
        )
        _inject_mock_server(adapter, mock_server)

        with pytest.raises(AuthError, match="No authorization code"):
            adapter.wait_for_callback(session)

    def test_returns_code_on_success(
        self, adapter: Auth0PkceAdapter, session: PkceSession
    ):
        mock_server = MagicMock()
        mock_server.wait_for_callback.return_value = CallbackResult(
            code="auth-code-123",
            state="test-state",
        )
        _inject_mock_server(adapter, mock_server)

        code = adapter.wait_for_callback(session)
        assert code == "auth-code-123"


class TestShutdownCallbackServer:
    def test_shutdown_when_server_exists(self, adapter: Auth0PkceAdapter):
        mock_server = MagicMock()
        _inject_mock_server(adapter, mock_server)

        adapter.shutdown_callback_server()

        mock_server.shutdown.assert_called_once()

    def test_shutdown_when_no_server(self, adapter: Auth0PkceAdapter):
        # Should not raise
        adapter.shutdown_callback_server()

    def test_shutdown_is_idempotent(self, adapter: Auth0PkceAdapter):
        mock_server = MagicMock()
        _inject_mock_server(adapter, mock_server)

        adapter.shutdown_callback_server()
        adapter.shutdown_callback_server()

        mock_server.shutdown.assert_called_once()

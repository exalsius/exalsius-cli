"""Unit tests for the `exls get-token` command."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from exls.app import app
from exls.auth.adapters.bundle import AuthBundle
from exls.auth.core.domain import AuthSession, LoadedToken, User
from exls.auth.core.service import AuthService, NotLoggedInWarning
from exls.shared.core.exceptions import ServiceError

runner = CliRunner()


@pytest.fixture
def auth_session() -> AuthSession:
    return AuthSession(
        user=User(email="a@b.c", nickname="alice", sub="auth0|123"),
        token=LoadedToken(
            client_id="client-id",
            access_token="my-access-token",
            id_token="id-token",
            refresh_token="refresh-token",
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        ),
    )


@pytest.fixture
def mock_service(auth_session: AuthSession) -> Mock:
    service = Mock(spec=AuthService)
    service.acquire_access_token.return_value = auth_session
    return service


def test_get_token_prints_raw_token_to_stdout(mock_service: Mock) -> None:
    with patch.object(AuthBundle, "get_auth_service", return_value=mock_service):
        result = runner.invoke(app, ["get-token"])

    assert result.exit_code == 0
    assert result.stdout == "my-access-token\n"


def test_get_token_json_format_emits_object(mock_service: Mock) -> None:
    with patch.object(AuthBundle, "get_auth_service", return_value=mock_service):
        result = runner.invoke(app, ["--format", "json", "get-token"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"access_token": "my-access-token"}


def test_get_token_not_logged_in_errors_to_stderr(mock_service: Mock) -> None:
    mock_service.acquire_access_token.side_effect = NotLoggedInWarning(
        "You are not logged in: no token"
    )

    with patch.object(AuthBundle, "get_auth_service", return_value=mock_service):
        result = runner.invoke(app, ["get-token"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "not logged in" in result.stderr.lower()


def test_get_token_service_error_errors_to_stderr(mock_service: Mock) -> None:
    mock_service.acquire_access_token.side_effect = ServiceError(
        message="Session is expired. Please log in again."
    )

    with patch.object(AuthBundle, "get_auth_service", return_value=mock_service):
        result = runner.invoke(app, ["get-token"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "failed to acquire access token" in result.stderr.lower()

from typing import Dict, Iterator
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import BaseModel, StrictStr

from exls.shared.adapters.http.commands import (
    HTTPCommandError,
    StreamingGetRequestCommand,
)
from exls.shared.core.ports.command import CommandError


class SampleModel(BaseModel):
    name: StrictStr
    value: StrictStr


class _TestStreamingCommand(StreamingGetRequestCommand[SampleModel]):
    def __init__(self, url: str, token: str):
        super().__init__(model=SampleModel)
        self._url = url
        self._token = token

    def _get_url(self) -> str:
        return self._url

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_yields_models(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = [
        '{"name": "event1", "value": "val1"}',
        '{"name": "event2", "value": "val2"}',
    ]
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    events: Iterator[SampleModel] = command.execute()
    result = list(events)

    assert len(result) == 2
    assert result[0].name == "event1"
    assert result[1].name == "event2"

    mock_get.assert_called_once_with(
        "https://example.com/stream",
        headers={"Authorization": "Bearer token123"},
        stream=True,
        timeout=(10, None),
    )


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_skips_empty_lines(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = [
        '{"name": "event1", "value": "val1"}',
        "",
        '{"name": "event2", "value": "val2"}',
    ]
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    result = list(command.execute())

    assert len(result) == 2


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_skips_malformed_json(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = [
        '{"name": "event1", "value": "val1"}',
        "not valid json",
        '{"name": "event2", "value": "val2"}',
    ]
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    result = list(command.execute())

    assert len(result) == 2
    assert result[0].name == "event1"
    assert result[1].name == "event2"


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_http_error(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "not found"}
    http_error = requests.exceptions.HTTPError(response=mock_response)
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")

    with pytest.raises(HTTPCommandError) as exc_info:
        command.execute()

    assert exc_info.value.status_code == 404


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_connection_error(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    command = _TestStreamingCommand("https://example.com/stream", "token123")

    with pytest.raises(CommandError):
        command.execute()


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_skips_validation_errors(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = [
        '{"name": "event1", "value": "val1"}',
        '{"name": 123, "value": "val2"}',
        '{"name": "event3", "value": "val3"}',
    ]
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    result = list(command.execute())

    assert len(result) == 2
    assert result[0].name == "event1"
    assert result[1].name == "event3"


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_close(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = iter([])
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    command.execute()
    command.close()

    mock_response.close.assert_called_once()


def _iter_one_then_chunked_error():
    yield '{"name": "event1", "value": "val1"}'
    raise requests.exceptions.ChunkedEncodingError("connection closed")


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_chunked_encoding_error_during_iteration(
    mock_get: MagicMock,
) -> None:
    """ChunkedEncodingError during iteration is treated as stream end; no exception."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = _iter_one_then_chunked_error()
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    events = command.execute()
    result = list(events)

    assert len(result) == 1
    assert result[0].name == "event1"


def _iter_one_then_connection_error():
    yield '{"name": "a", "value": "b"}'
    raise requests.exceptions.ConnectionError("connection reset")


@patch("exls.shared.adapters.http.commands.requests.get")
def test_streaming_command_connection_error_during_iteration(
    mock_get: MagicMock,
) -> None:
    """ConnectionError during iteration is treated as stream end; no exception."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_lines.return_value = _iter_one_then_connection_error()
    mock_get.return_value = mock_response

    command = _TestStreamingCommand("https://example.com/stream", "token123")
    events = command.execute()
    result = list(events)

    assert len(result) == 1
    assert result[0].name == "a"

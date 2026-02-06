import json
import logging
from abc import abstractmethod
from typing import Any, Dict, Iterator, Optional, Type, TypeVar, Union

import requests
from pydantic import BaseModel, ValidationError

from exls.shared.adapters.deserializer import PydanticDeserializer
from exls.shared.core.exceptions import ExalsiusWarning
from exls.shared.core.ports.command import BaseCommand, CommandError

logger = logging.getLogger(__name__)

T_SerOutput = TypeVar("T_SerOutput", bound=BaseModel)
T_SerOutput_Nullable = TypeVar("T_SerOutput_Nullable", bound=Union[BaseModel, None])


class HTTPCommandError(CommandError):
    def __init__(
        self,
        message: str,
        endpoint: str,
        status_code: int,
        error_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.endpoint: str = endpoint
        self.status_code: int = status_code
        self.error_body: Optional[Dict[str, Any]] = error_body


class UnexpectedHttpResponseWarning(ExalsiusWarning):
    def __init__(self, message: str):
        super().__init__(message)


class BasePostRequestCommand(BaseCommand[T_SerOutput_Nullable]):
    """Base class for POST request commands with shared request logic."""

    @abstractmethod
    def _get_url(self) -> str:
        """Return the URL for the POST request."""
        pass

    @abstractmethod
    def _get_payload(self) -> Dict[str, Any]:
        """Return the payload for the POST request."""
        pass

    def _make_post_request(self) -> requests.Response:
        """Execute the POST request and return the raw response."""
        url: str = self._get_url()
        try:
            payload: Dict[str, Any] = self._get_payload()
            response: requests.Response = requests.post(url, data=payload)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            error_body: Optional[Dict[str, Any]] = None
            try:
                error_body = e.response.json()
            except requests.exceptions.JSONDecodeError:
                pass
            raise HTTPCommandError(
                message=f"error making POST request to {url}: {e}",
                endpoint=url,
                status_code=e.response.status_code,
                error_body=error_body,
            ) from e
        except Exception as e:
            raise CommandError(
                message=f"unexpected error making POST request to {url}: {e}"
            ) from e


class PostRequestWithResponseCommand(BasePostRequestCommand[T_SerOutput]):
    """Command for POST requests that expect a JSON response."""

    def __init__(
        self,
        model: Type[T_SerOutput],
        deserializer: PydanticDeserializer[T_SerOutput] = PydanticDeserializer(),
    ):
        self._model: Type[T_SerOutput] = model
        self._deserializer: PydanticDeserializer[T_SerOutput] = deserializer

    def execute(self) -> T_SerOutput:
        response: requests.Response = self._make_post_request()
        if response.headers.get("Content-Length") == "0":
            raise UnexpectedHttpResponseWarning(
                f"unexpected response from post request to {self._get_url()}: "
                f"expected json response of model {self._model.__name__} but response content is empty."
            )
        deserialized_response: T_SerOutput = self._deserializer.deserialize(
            response.json(), self._model
        )
        return deserialized_response


class PostRequestWithoutResponseCommand(BasePostRequestCommand[None]):
    """Command for POST requests that expect no response body (204)."""

    def execute(self) -> None:
        response: requests.Response = self._make_post_request()

        if response.content and response.headers.get("Content-Length") != "0":
            raise UnexpectedHttpResponseWarning(
                f"unexpected response from post request to {self._get_url()}: "
                f"expected empty response but got content: {response.content}"
            )


class StreamingGetRequestCommand(BaseCommand[Iterator[T_SerOutput]]):
    """Base class for streaming GET requests that yield NDJSON lines as Pydantic models."""

    def __init__(self, model: Type[T_SerOutput]):
        self._model: Type[T_SerOutput] = model
        self._response: Optional[requests.Response] = None

    @abstractmethod
    def _get_url(self) -> str:
        """Return the URL for the GET request."""
        pass

    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Return the headers for the GET request."""
        pass

    def execute(self) -> Iterator[T_SerOutput]:
        url: str = self._get_url()
        try:
            self._response = requests.get(
                url,
                headers=self._get_headers(),
                stream=True,
                timeout=(10, None),
            )
            self._response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_body: Optional[Dict[str, Any]] = None
            try:
                error_body = e.response.json()
            except requests.exceptions.JSONDecodeError:
                pass
            raise HTTPCommandError(
                message=f"error making streaming GET request to {url}: {e}",
                endpoint=url,
                status_code=e.response.status_code,
                error_body=error_body,
            ) from e
        except Exception as e:
            raise CommandError(
                message=f"unexpected error making streaming GET request to {url}: {e}"
            ) from e

        return self._iter_lines()

    def _iter_lines(self) -> Iterator[T_SerOutput]:
        assert self._response is not None
        try:
            for line in self._response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data: Dict[str, Any] = json.loads(line)
                    yield self._model.model_validate(data)
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.warning(f"skipping malformed NDJSON line: {e}")
                    continue
        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
        ) as e:
            logger.debug("stream ended: %s", e)
            return

    def close(self) -> None:
        if self._response is not None:
            self._response.close()
            self._response = None

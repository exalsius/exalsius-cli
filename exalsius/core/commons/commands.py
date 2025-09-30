from abc import abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Union

import requests
from pydantic import BaseModel

from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.exceptions import ExalsiusError, ExalsiusWarning
from exalsius.core.commons.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)

T_SerOutput = TypeVar("T_SerOutput", bound=BaseModel)
T_SerOutput_Nullable = TypeVar("T_SerOutput_Nullable", bound=Union[BaseModel, None])


class NetworkError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)


class UnexpectedHttpResponseWarning(ExalsiusWarning):
    def __init__(self, message: str):
        super().__init__(message)


class AuthenticationError(ExalsiusError):
    def __init__(self, message: str):
        super().__init__(message)


class ResourceNotFoundError(ExalsiusError):
    def __init__(self, resource_type: str, endpoint: str):
        super().__init__(f"{resource_type} not found at {endpoint}")


class APIError(ExalsiusError):
    def __init__(self, message: str, endpoint: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message: str = message
        self.endpoint: str = endpoint
        self.status_code: Optional[int] = status_code


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
            if e.response.status_code == 401:
                raise AuthenticationError(
                    f"Invalid or expired credentials for {url}"
                ) from e
            elif e.response.status_code == 404:
                raise ResourceNotFoundError("resource", url) from e
            else:
                raise APIError(
                    f"Error making POST request to {url}: {e.response.text}",
                    url,
                    e.response.status_code,
                ) from e
        except DeserializationError as e:
            raise APIError(
                f"Error deserializing response from {url}: {e}",
                url,
            ) from e
        except Exception as e:
            raise APIError(f"Error making POST request to {url}: {e}", url) from e


class PostRequestWithResponseCommand(BasePostRequestCommand[T_SerOutput]):
    """Command for POST requests that expect a JSON response."""

    __error_message_template = "unexpected response from post request to {}"

    def __init__(
        self, model: Type[T_SerOutput], deserializer: PydanticDeserializer[T_SerOutput]
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

        # Optionally validate 204 status if that's your API contract
        if response.content and response.headers.get("Content-Length") != "0":
            raise UnexpectedHttpResponseWarning(
                f"unexpected response from post request to {self._get_url()}: "
                f"expected empty response but got content: {response.content}"
            )

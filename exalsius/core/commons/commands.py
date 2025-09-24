from abc import abstractmethod
from typing import Any, Dict, Type

import requests

from exalsius.core.base.commands import BaseCommand
from exalsius.core.commons.models import (
    SaveFileRequestDTO,
    SaveFileResponseDTO,
    UnexpectedResponseWarning,
)


class PostRequestCommand(BaseCommand):
    __error_message_template = "unexpected response from post request to {}"

    @abstractmethod
    def _get_url(self) -> str:
        pass

    @abstractmethod
    def _get_payload(self) -> Dict[str, Any]:
        pass

    def _execute_post_request(self, model: Type[Any]) -> Any:
        url: str = self._get_url()
        payload: Dict[str, Any] = self._get_payload()
        response: requests.Response = requests.post(url, data=payload)
        response.raise_for_status()
        if response.headers.get("Content-Type") == "application/json":
            data: Any = self._deserialize(response.json(), model)
        elif (
            response.status_code == 204 or response.headers.get("Content-Length") == "0"
        ):
            raise UnexpectedResponseWarning(
                self.__error_message_template.format(url)
                + f": unexpected response. expected {model.__name__} object but "
                f"response content is empty."
            )
        else:
            raise UnexpectedResponseWarning(
                self.__error_message_template.format(url)
                + f": expected json content as {model.__name__} object "
                f"but got {response.headers.get('Content-Type')}. cannot deserialize response content."
            )

        return data

    def _execute_post_request_empty_response(self) -> None:
        response: requests.Response = requests.post(
            self._get_url(), data=self._get_payload()
        )
        response.raise_for_status()


class SaveFileCommand(BaseCommand):
    def __init__(self, request: SaveFileRequestDTO):
        self.request: SaveFileRequestDTO = request

    def execute(self) -> SaveFileResponseDTO:
        with open(self.request.file_path, "w") as file:
            file.write(self.request.content)

        return SaveFileResponseDTO(file_path=self.request.file_path)

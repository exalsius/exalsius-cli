from abc import abstractmethod
from typing import Any, Dict, Generic, Type

import requests

from exalsius.core.base.commands import BaseCommand, T


class PostRequestCommand(BaseCommand[T], Generic[T]):
    @abstractmethod
    def _get_url(self) -> str:
        pass

    @abstractmethod
    def _get_payload(self) -> Dict[str, Any]:
        pass

    def _execute_post_request(self, model: Type[T]) -> T:
        response: requests.Response = requests.post(
            self._get_url(), data=self._get_payload()
        )
        response.raise_for_status()
        return self._deserialize(response.json(), model)

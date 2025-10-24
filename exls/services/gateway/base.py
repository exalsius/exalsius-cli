from abc import ABC, abstractmethod
from typing import List

from exls.services.domain import Service


class ServicesGateway(ABC):
    @abstractmethod
    def list(self, cluster_id: str) -> List[Service]:
        raise NotImplementedError

    @abstractmethod
    def get(self, service_id: str) -> Service:
        raise NotImplementedError

    @abstractmethod
    def delete(self, service_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def deploy(self) -> str:
        raise NotImplementedError

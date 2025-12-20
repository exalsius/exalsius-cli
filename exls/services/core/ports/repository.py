from abc import ABC, abstractmethod
from typing import List

from exls.services.core.domain import Service


class ServiceRepository(ABC):
    @abstractmethod
    def list(self, cluster_id: str) -> List[Service]: ...

    @abstractmethod
    def get(self, service_id: str) -> Service: ...

    @abstractmethod
    def delete(self, service_id: str) -> str: ...

from abc import ABC, abstractmethod


class ServiceOperations(ABC):
    @abstractmethod
    def deploy(self) -> str: ...

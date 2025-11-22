from abc import ABC, abstractmethod
from typing import Optional


class IServiceInputManager(ABC):
    @abstractmethod
    def ask_service_name(self, default: Optional[str] = None) -> str: ...

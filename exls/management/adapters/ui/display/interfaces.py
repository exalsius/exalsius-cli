from abc import ABC, abstractmethod
from typing import Optional


class IManagementInputManager(ABC):
    @abstractmethod
    def ask_ssh_key_name(self, default: Optional[str] = None) -> str: ...

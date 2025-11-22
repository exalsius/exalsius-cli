from abc import ABC, abstractmethod
from typing import Optional


class INodesInputManager(ABC):
    @abstractmethod
    def ask_node_name(self, default: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def ask_node_endpoint(self) -> str:
        pass

    @abstractmethod
    def ask_node_username(self, default: Optional[str] = None) -> str:
        pass

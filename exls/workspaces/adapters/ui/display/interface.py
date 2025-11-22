from abc import ABC, abstractmethod
from typing import Optional


class IWorkspaceInputManager(ABC):
    @abstractmethod
    def ask_workspace_name(self, default: Optional[str] = None) -> str: ...

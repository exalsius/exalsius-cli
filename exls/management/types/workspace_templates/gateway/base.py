from abc import ABC, abstractmethod
from typing import List

from exls.management.types.workspace_templates.domain import WorkspaceTemplate


class WorkspaceTemplatesGateway(ABC):
    @abstractmethod
    def list(self) -> List[WorkspaceTemplate]:
        raise NotImplementedError

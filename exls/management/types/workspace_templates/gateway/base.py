from abc import ABC, abstractmethod
from typing import List

from exls.management.types.workspace_templates.domain import (
    WorkspaceTemplate,
    WorkspaceTemplateFilterParams,
)


class WorkspaceTemplatesGateway(ABC):
    @abstractmethod
    def list(self, params: WorkspaceTemplateFilterParams) -> List[WorkspaceTemplate]:
        raise NotImplementedError

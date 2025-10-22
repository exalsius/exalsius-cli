from abc import ABC, abstractmethod
from typing import List

from exls.management.types.cluster_templates.domain import (
    ClusterTemplate,
    ClusterTemplateFilterParams,
)


class ClusterTemplatesGateway(ABC):
    @abstractmethod
    def list(self, params: ClusterTemplateFilterParams) -> List[ClusterTemplate]:
        raise NotImplementedError

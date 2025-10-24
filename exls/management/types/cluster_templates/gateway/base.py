from abc import ABC, abstractmethod
from typing import List

from exls.management.types.cluster_templates.domain import (
    ClusterTemplate,
)


class ClusterTemplatesGateway(ABC):
    @abstractmethod
    def list(self) -> List[ClusterTemplate]:
        raise NotImplementedError

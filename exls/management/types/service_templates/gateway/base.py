from abc import ABC, abstractmethod
from typing import List

from exls.management.types.service_templates.domain import (
    ServiceTemplate,
)


class ServiceTemplatesGateway(ABC):
    @abstractmethod
    def list(self) -> List[ServiceTemplate]:
        raise NotImplementedError

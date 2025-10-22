from abc import ABC, abstractmethod
from typing import List

from exls.management.types.service_templates.domain import (
    ServiceTemplate,
    ServiceTemplateFilterParams,
)


class ServiceTemplatesGateway(ABC):
    @abstractmethod
    def list(self, params: ServiceTemplateFilterParams) -> List[ServiceTemplate]:
        raise NotImplementedError

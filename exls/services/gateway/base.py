from abc import ABC, abstractmethod
from typing import List

from exls.services.domain import Service, ServiceDeployParams, ServiceFilterParams


class ServicesGateway(ABC):
    @abstractmethod
    def list(self, service_filter_params: ServiceFilterParams) -> List[Service]:
        raise NotImplementedError

    @abstractmethod
    def get(self, service_id: str) -> Service:
        raise NotImplementedError

    @abstractmethod
    def delete(self, service_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, deploy_params: ServiceDeployParams) -> str:
        raise NotImplementedError

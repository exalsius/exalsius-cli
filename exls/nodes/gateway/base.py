from abc import ABC, abstractmethod
from typing import List

from exls.nodes.domain import (
    BaseNode,
    ImportFromOfferParams,
    ImportSshParams,
    NodeFilterParams,
)


class NodesGateway(ABC):
    @abstractmethod
    def list(self, node_filter_params: NodeFilterParams) -> List[BaseNode]:
        raise NotImplementedError

    @abstractmethod
    def get(self, node_id: str) -> BaseNode:
        raise NotImplementedError

    @abstractmethod
    def delete(self, node_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def import_ssh(self, import_ssh_params: ImportSshParams) -> BaseNode:
        raise NotImplementedError

    @abstractmethod
    def import_from_offer(
        self, import_from_offer_params: ImportFromOfferParams
    ) -> List[BaseNode]:
        raise NotImplementedError

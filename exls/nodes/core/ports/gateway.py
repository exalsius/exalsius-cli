from abc import ABC, abstractmethod
from typing import List

from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
)


class INodesGateway(ABC):
    @abstractmethod
    def list(self, filter: NodesFilterCriteria) -> List[BaseNode]: ...

    @abstractmethod
    def get(self, node_id: str) -> BaseNode: ...

    @abstractmethod
    def delete(self, node_id: str) -> str: ...

    @abstractmethod
    def import_selfmanaged_node(self, request: ImportSelfmanagedNodeRequest) -> str: ...

    @abstractmethod
    def import_cloud_nodes(self, request: ImportCloudNodeRequest) -> List[str]: ...

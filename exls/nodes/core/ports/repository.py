from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from exls.nodes.core.domain import BaseNode
from exls.nodes.core.requests import NodesFilterCriteria


class NodesRepository(ABC):
    @abstractmethod
    def list(self, filter: Optional[NodesFilterCriteria]) -> List[BaseNode]: ...

    @abstractmethod
    def get(self, node_id: str) -> BaseNode: ...

    @abstractmethod
    def delete(self, node_id: str) -> str: ...

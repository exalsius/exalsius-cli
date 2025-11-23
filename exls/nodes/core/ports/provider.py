from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, StrictStr


class NodeSshKey(BaseModel):
    id: StrictStr = Field(..., description="The ID of the SSH key")
    name: StrictStr = Field(..., description="The name of the SSH key")


class ISshKeyProvider(ABC):
    @abstractmethod
    def list_keys(self) -> List[NodeSshKey]: ...

    @abstractmethod
    def add_key(self, name: str, key_path: Path) -> NodeSshKey: ...

from abc import ABC, abstractmethod
from typing import Optional


class IClusterInputManager(ABC):
    @abstractmethod
    def ask_cluster_name(self, default: Optional[str] = None) -> str: ...

    @abstractmethod
    def ask_cluster_type(self, default: Optional[str] = None) -> str: ...

    @abstractmethod
    def ask_gpu_type(self, default: Optional[str] = None) -> str: ...

    @abstractmethod
    def ask_enable_multinode_training(self, default: Optional[bool] = None) -> bool: ...

    @abstractmethod
    def ask_enable_telemetry(self, default: Optional[bool] = None) -> bool: ...

"""Device Code authentication flow operations."""

from abc import ABC, abstractmethod
from typing import Optional

from exls.auth.core.domain import DeviceCode, Token


class DeviceCodeOperations(ABC):
    @abstractmethod
    def fetch_device_code(self, organization: Optional[str] = None) -> DeviceCode: ...

    @abstractmethod
    def poll_for_authentication(self, device_code: DeviceCode) -> Token: ...

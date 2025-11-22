from abc import ABC, abstractmethod

from exls.auth.adapters.dtos import DeviceCodeAuthenticationDTO


class IAuthInputManager(ABC):
    @abstractmethod
    def display_auth_poling(self, dto: DeviceCodeAuthenticationDTO) -> None: ...

from abc import ABC, abstractmethod
from typing import List

from exls.management.core.domain import (
    SshKey,
    WorkspaceTemplate,
)


class ManagementRepository(ABC):
    @abstractmethod
    def list_workspace_templates(self) -> List[WorkspaceTemplate]: ...

    @abstractmethod
    def list_ssh_keys(self) -> List[SshKey]: ...

    @abstractmethod
    def create_ssh_key(
        self, name: str, base64_key_content: str, scope: str = "private"
    ) -> str: ...

    @abstractmethod
    def delete_ssh_key(self, ssh_key_id: str) -> str: ...

    @abstractmethod
    def get_dashboard_url(self) -> str: ...

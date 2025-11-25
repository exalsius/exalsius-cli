from abc import ABC, abstractmethod
from typing import List

from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)


class IManagementGateway(ABC):
    @abstractmethod
    def list_cluster_templates(self) -> List[ClusterTemplate]: ...

    @abstractmethod
    def list_credentials(self) -> List[Credentials]: ...

    @abstractmethod
    def list_service_templates(self) -> List[ServiceTemplate]: ...

    @abstractmethod
    def list_workspace_templates(self) -> List[WorkspaceTemplate]: ...

    @abstractmethod
    def list_ssh_keys(self) -> List[SshKey]: ...

    @abstractmethod
    def import_ssh_key(self, name: str, base64_key_content: str) -> str: ...

    @abstractmethod
    def delete_ssh_key(self, ssh_key_id: str) -> str: ...

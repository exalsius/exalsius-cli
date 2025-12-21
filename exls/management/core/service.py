from pathlib import Path
from typing import List, Optional

from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)
from exls.management.core.ports.ports import ManagementRepository
from exls.shared.core.decorators import handle_service_layer_errors
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.ports.file import FileReadPort


class ManagementService:
    def __init__(
        self,
        management_repository: ManagementRepository,
        file_read_adapter: FileReadPort[str],
    ):
        self._management_repository: ManagementRepository = management_repository
        self._file_read_adapter: FileReadPort[str] = file_read_adapter

    @handle_service_layer_errors("listing cluster templates")
    def list_cluster_templates(self) -> List[ClusterTemplate]:
        return self._management_repository.list_cluster_templates()

    @handle_service_layer_errors("listing credentials")
    def list_credentials(self) -> List[Credentials]:
        return self._management_repository.list_credentials()

    @handle_service_layer_errors("listing service templates")
    def list_service_templates(self) -> List[ServiceTemplate]:
        return self._management_repository.list_service_templates()

    @handle_service_layer_errors("listing workspace templates")
    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        return self._management_repository.list_workspace_templates()

    @handle_service_layer_errors("listing ssh keys")
    def list_ssh_keys(self) -> List[SshKey]:
        return self._management_repository.list_ssh_keys()

    @handle_service_layer_errors("importing ssh key")
    def import_ssh_key(self, name: str, key_path: Path) -> SshKey:
        key_content_base64: str = self._file_read_adapter.read_file(file_path=key_path)
        ssh_key_id: str = self._management_repository.create_ssh_key(
            name=name, base64_key_content=key_content_base64
        )
        ssh_keys: List[SshKey] = self._management_repository.list_ssh_keys()
        ssh_key: Optional[SshKey] = next(
            (ssh_key for ssh_key in ssh_keys if ssh_key.id == ssh_key_id), None
        )
        if ssh_key is None:
            raise ServiceError(
                message=f"Unexpected error: SSH key {name} was not imported"
            )
        return ssh_key

    @handle_service_layer_errors("deleting ssh key")
    def delete_ssh_key(self, ssh_key_id: str) -> str:
        return self._management_repository.delete_ssh_key(ssh_key_id)

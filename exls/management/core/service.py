from typing import List, Optional

from exls.management.core.domain import (
    AddSshKeyRequest,
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)
from exls.management.core.ports import IManagementGateway
from exls.shared.adapters.decorators import handle_service_errors
from exls.shared.adapters.gateway.file.gateways import IFileReadGateway
from exls.shared.core.service import ServiceError


class ManagementService:
    def __init__(
        self,
        management_gateway: IManagementGateway,
        fileio_gateway: IFileReadGateway[str],
    ):
        self.management_gateway: IManagementGateway = management_gateway
        self.fileio_gateway: IFileReadGateway[str] = fileio_gateway

    @handle_service_errors("listing cluster templates")
    def list_cluster_templates(self) -> List[ClusterTemplate]:
        return self.management_gateway.list_cluster_templates()

    @handle_service_errors("listing credentials")
    def list_credentials(self) -> List[Credentials]:
        return self.management_gateway.list_credentials()

    @handle_service_errors("listing service templates")
    def list_service_templates(self) -> List[ServiceTemplate]:
        return self.management_gateway.list_service_templates()

    @handle_service_errors("listing workspace templates")
    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        return self.management_gateway.list_workspace_templates()

    @handle_service_errors("listing ssh keys")
    def list_ssh_keys(self) -> List[SshKey]:
        return self.management_gateway.list_ssh_keys()

    @handle_service_errors("adding ssh key")
    def add_ssh_key(self, request: AddSshKeyRequest) -> SshKey:
        key_content_base64: str = self.fileio_gateway.read_file(
            file_path=request.key_path
        )
        ssh_key_id: str = self.management_gateway.add_ssh_key(
            name=request.name, base64_key_content=key_content_base64
        )
        ssh_keys: List[SshKey] = self.management_gateway.list_ssh_keys()
        ssh_key: Optional[SshKey] = next(
            (ssh_key for ssh_key in ssh_keys if ssh_key.id == ssh_key_id), None
        )
        if ssh_key is None:
            raise ServiceError(
                message=f"Unexpected error: SSH key {request.name} was not added"
            )
        return ssh_key

    @handle_service_errors("deleting ssh key")
    def delete_ssh_key(self, ssh_key_id: str) -> str:
        return self.management_gateway.delete_ssh_key(ssh_key_id)

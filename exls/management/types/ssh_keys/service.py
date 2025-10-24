from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.core.commons.gateways.fileio import StringFileIOGateway
from exls.management.types.ssh_keys.dtos import (
    AddSshKeyRequestDTO,
    ListSshKeysRequestDTO,
    SshKeyDTO,
)
from exls.management.types.ssh_keys.gateway.base import SshKeysGateway
from exls.management.types.ssh_keys.gateway.dtos import AddSshKeyParams

SSH_KEYS_API_ERROR_TYPE: str = "SshKeysApiError"


class SshKeysService:
    def __init__(
        self,
        ssh_keys_gateway: SshKeysGateway,
        file_io_gateway: StringFileIOGateway,
    ):
        self.ssh_keys_gateway = ssh_keys_gateway
        self.file_io_gateway = file_io_gateway

    @handle_service_errors("listing ssh keys")
    def list_ssh_keys(self, request: ListSshKeysRequestDTO) -> List[SshKeyDTO]:
        ssh_keys = self.ssh_keys_gateway.list()
        return [SshKeyDTO.from_domain(key) for key in ssh_keys]

    @handle_service_errors("adding ssh key")
    def add_ssh_key(self, request: AddSshKeyRequestDTO) -> str:
        # This might be lower level than the service layer, but it's ok for now.
        private_key_base64: str = self.file_io_gateway.read_file_base64(
            request.key_path
        )
        add_ssh_key_params = AddSshKeyParams(
            name=request.name, private_key_base64=private_key_base64
        )
        return self.ssh_keys_gateway.create(add_ssh_key_params)

    @handle_service_errors("deleting ssh key")
    def delete_ssh_key(self, ssh_key_id: str) -> None:
        self.ssh_keys_gateway.delete(ssh_key_id)


def get_ssh_keys_service(config: AppConfig, access_token: str) -> SshKeysService:
    gateway_factory: GatewayFactory = GatewayFactory(config=config)
    ssh_keys_gateway: SshKeysGateway = gateway_factory.create_ssh_keys_gateway(
        access_token=access_token
    )
    file_io_gateway: StringFileIOGateway = (
        gateway_factory.create_string_fileio_gateway()
    )
    return SshKeysService(
        ssh_keys_gateway=ssh_keys_gateway,
        file_io_gateway=file_io_gateway,
    )

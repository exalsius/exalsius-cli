import pathlib
from typing import Optional

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth, T
from exalsius.core.commons.models import ServiceError
from exalsius.nodes.commands import (
    AddSSHKeyCommand,
    DeleteNodeCommand,
    DeleteSSHKeyCommand,
    GetNodeCommand,
    ImportFromOfferCommand,
    ImportSSHNodeCommand,
    ListNodesCommand,
    ListSSHKeysCommand,
)
from exalsius.nodes.models import (
    CloudProvider,
    NodesDeleteRequestDTO,
    NodesGetRequestDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    NodeType,
    SSHKeysAddRequestDTO,
    SSHKeysDeleteRequestDTO,
    SSHKeysDeleteResultDTO,
    SSHKeysListRequestDTO,
)


class NodeService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.nodes_api: NodesApi = NodesApi(self.api_client)
        self.management_api: ManagementApi = ManagementApi(self.api_client)

    def _execute_command(self, command: BaseCommand[T]) -> T:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                f"api error while executing command {command.__class__.__name__}. "
                f"Error code: {e.status}, error body: {e.body}"
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {e}"
            )

    def list_nodes(
        self, node_type: Optional[NodeType], provider: Optional[CloudProvider]
    ) -> NodesListResponse:
        return self._execute_command(
            ListNodesCommand(
                NodesListRequestDTO(
                    api=self.nodes_api,
                    node_type=node_type,
                    provider=provider,
                )
            )
        )

    def get_node(self, node_id: str) -> NodeResponse:
        return self._execute_command(
            GetNodeCommand(
                NodesGetRequestDTO(
                    api=self.nodes_api,
                    node_id=node_id,
                )
            )
        )

    def delete_node(self, node_id: str) -> NodeDeleteResponse:
        return self._execute_command(
            DeleteNodeCommand(
                NodesDeleteRequestDTO(
                    api=self.nodes_api,
                    node_id=node_id,
                )
            )
        )

    def import_ssh(
        self, hostname: str, endpoint: str, username: str, ssh_key_id: str
    ) -> NodeImportResponse:
        return self._execute_command(
            ImportSSHNodeCommand(
                NodesImportSSHRequestDTO(
                    api=self.nodes_api,
                    hostname=hostname,
                    endpoint=endpoint,
                    username=username,
                    ssh_key_id=ssh_key_id,
                )
            )
        )

    def import_from_offer(
        self, hostname: str, offer_id: str, amount: int
    ) -> NodeImportResponse:
        return self._execute_command(
            ImportFromOfferCommand(
                NodesImportFromOfferRequestDTO(
                    api=self.nodes_api,
                    hostname=hostname,
                    offer_id=offer_id,
                    amount=amount,
                )
            )
        )

    def add_ssh_key(self, name: str, key_path: pathlib.Path) -> SshKeyCreateResponse:
        if not (key_path.exists() and key_path.is_file()):
            raise ServiceError(
                f"SSH key file {key_path} does not exist or is not a file"
            )

        return self._execute_command(
            AddSSHKeyCommand(
                SSHKeysAddRequestDTO(
                    api=self.management_api,
                    name=name,
                    key_path=str(key_path),
                )
            )
        )

    def list_ssh_keys(self) -> SshKeysListResponse:
        return self._execute_command(
            ListSSHKeysCommand(
                SSHKeysListRequestDTO(
                    api=self.management_api,
                )
            )
        )

    def delete_ssh_key(self, name: str) -> SSHKeysDeleteResultDTO:
        return self._execute_command(
            DeleteSSHKeyCommand(
                SSHKeysDeleteRequestDTO(
                    api=self.management_api,
                    name=name,
                )
            )
        )

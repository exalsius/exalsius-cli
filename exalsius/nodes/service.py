import pathlib
from typing import List, Optional, Tuple

from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.ssh_key import SshKey
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse

from exalsius.base.service import BaseServiceWithAuth
from exalsius.clusters.models import CloudProvider
from exalsius.nodes.models import NodeType
from exalsius.nodes.operations import (
    AddSSHKeyOperation,
    DeleteNodeOperation,
    DeleteSSHKeyOperation,
    GetNodeOperation,
    ImportFromOfferOperation,
    ImportSSHNodeOperation,
    ListNodesOperation,
    ListSSHKeysOperation,
)


class NodeService(BaseServiceWithAuth):
    def list_nodes(
        self, node_type: Optional[NodeType], provider: Optional[CloudProvider]
    ) -> Tuple[List[NodeResponse], Optional[str]]:
        return self.execute_operation(
            ListNodesOperation(
                self.api_client,
                node_type,
                provider,
            )
        )

    def get_node(self, node_id: str) -> Tuple[Optional[NodeResponse], Optional[str]]:
        return self.execute_operation(
            GetNodeOperation(
                self.api_client,
                node_id,
            )
        )

    def delete_node(
        self, node_id: str
    ) -> Tuple[Optional[NodeDeleteResponse], Optional[str]]:
        return self.execute_operation(
            DeleteNodeOperation(
                self.api_client,
                node_id,
            )
        )

    def import_ssh(
        self, hostname: str, endpoint: str, username: str, ssh_key_id: str
    ) -> Tuple[Optional[NodeImportResponse], Optional[str]]:
        return self.execute_operation(
            ImportSSHNodeOperation(
                self.api_client,
                hostname,
                endpoint,
                username,
                ssh_key_id,
            )
        )

    def import_from_offer(
        self, hostname: str, offer_id: str, amount: int
    ) -> Tuple[Optional[NodeImportResponse], Optional[str]]:
        return self.execute_operation(
            ImportFromOfferOperation(
                self.api_client,
                hostname,
                offer_id,
                amount,
            )
        )

    def add_ssh_key(
        self, name: str, key_path: pathlib.Path
    ) -> Tuple[Optional[SshKeyCreateResponse], Optional[str]]:
        if not key_path.exists():
            return None, f"SSH key file {key_path} does not exist"

        if not key_path.is_file():
            return None, f"SSH key file {key_path} is not a file"

        key_path_str = str(key_path)

        return self.execute_operation(
            AddSSHKeyOperation(
                self.api_client,
                name,
                key_path_str,
            )
        )

    def list_ssh_keys(self) -> Tuple[List[SshKey], Optional[str]]:
        return self.execute_operation(ListSSHKeysOperation(self.api_client))

    def delete_ssh_key(self, name: str) -> Tuple[bool, Optional[str]]:
        return self.execute_operation(
            DeleteSSHKeyOperation(
                self.api_client,
                name,
            )
        )

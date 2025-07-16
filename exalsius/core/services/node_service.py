from typing import List, Optional, Tuple

from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_response import NodeResponse

from exalsius.core.models.enums import CloudProvider, NodeType
from exalsius.core.operations.node_operations import (
    DeleteNodeOperation,
    GetNodeOperation,
    ImportFromOfferOperation,
    ImportSSHNodeOperation,
    ListNodesOperation,
)
from exalsius.core.services.base import BaseServiceWithAuth


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

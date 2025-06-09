from typing import List, Optional, Tuple

from exalsius_api_client.models.base_node import BaseNode

from exalsius.cli.commands.nodes import CloudProvider, NodeType
from exalsius.core.operations.node_operations import ListNodesOperation
from exalsius.core.services.base import BaseService


class NodeService(BaseService):
    def list_nodes(
        self, node_type: Optional[NodeType], provider: Optional[CloudProvider]
    ) -> Tuple[List[BaseNode], Optional[str]]:
        return self.execute_operation(
            ListNodesOperation(
                self.api_client,
                node_type,
                provider,
            )
        )

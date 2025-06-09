from typing import List, Optional, Tuple

import exalsius_api_client
from exalsius_api_client import NodesApi
from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exalsius.core.models.enums import CloudProvider, NodeType
from exalsius.core.operations.base import ListOperation


class ListNodesOperation(ListOperation[BaseNode]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        node_type: NodeType,
        provider: CloudProvider,
    ):
        self.api_client = api_client
        self.node_type = node_type
        self.provider = provider

    def execute(self) -> Tuple[List[BaseNode], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            nodes_list_response: NodesListResponse = api_instance.list_nodes(
                node_type=self.node_type,
                provider=self.provider,
            )
        except Exception as e:
            print(e)
            return None, str(e)
        return nodes_list_response.nodes, None

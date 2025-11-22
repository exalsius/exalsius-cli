from typing import List, cast

from exls.nodes.core.domain import BaseNode, CloudNode, SelfManagedNode
from exls.nodes.core.ports import INodesGateway
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.decorators import handle_service_errors
from exls.shared.core.service import ServiceError


class NodesService:
    def __init__(self, nodes_gateway: INodesGateway):
        self.nodes_gateway: INodesGateway = nodes_gateway

    @handle_service_errors("listing nodes")
    def list_nodes(self, request: NodesFilterCriteria) -> List[BaseNode]:
        assert request is not None
        return self.nodes_gateway.list(request)

    @handle_service_errors("getting node")
    def get_node(self, node_id: str) -> BaseNode:
        return self.nodes_gateway.get(node_id)

    @handle_service_errors("deleting node")
    def delete_node(self, node_id: str) -> str:
        return self.nodes_gateway.delete(node_id)

    @handle_service_errors("importing self-managed nodes")
    def import_selfmanaged_nodes(
        self, node_import_requests: List[ImportSelfmanagedNodeRequest]
    ) -> List[SelfManagedNode]:
        if len(node_import_requests) == 0:
            raise ServiceError(
                message="Self-managed import request must contain at least one node to import"
            )
        node_ids: List[str] = [
            self.nodes_gateway.import_selfmanaged_node(node_import_request)
            for node_import_request in node_import_requests
        ]

        nodes: List[SelfManagedNode] = [
            cast(SelfManagedNode, self.nodes_gateway.get(node_id))
            for node_id in node_ids
        ]

        return nodes

    @handle_service_errors("importing cloud nodes")
    def import_cloud_nodes(self, request: ImportCloudNodeRequest) -> List[CloudNode]:
        node_ids: List[str] = self.nodes_gateway.import_cloud_nodes(request)
        nodes: List[CloudNode] = [
            cast(CloudNode, self.nodes_gateway.get(node_id)) for node_id in node_ids
        ]
        return nodes

from typing import List

from exls.config import AppConfig
from exls.core.base.service import ServiceError
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.nodes.domain import BaseNode
from exls.nodes.dtos import (
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    node_dto_from_domain,
)
from exls.nodes.gateway.base import NodesGateway
from exls.nodes.gateway.dtos import (
    AllowedNodeStatusFilters,
    ImportFromOfferParams,
    NodeFilterParams,
    NodeImportSshParams,
)


class NodeService:
    def __init__(self, nodes_gateway: NodesGateway):
        self.nodes_gateway: NodesGateway = nodes_gateway

    @handle_service_errors("listing nodes")
    def list_nodes(self, request: NodesListRequestDTO) -> List[NodeDTO]:
        assert request is not None
        node_filter_params: NodeFilterParams = NodeFilterParams(
            node_type=request.node_type.value if request.node_type else None,
            status=(
                AllowedNodeStatusFilters(request.status.value.upper())
                if request.status is not None
                else None
            ),
        )
        nodes: List[BaseNode] = self.nodes_gateway.list(node_filter_params)
        return [node_dto_from_domain(node) for node in nodes]

    @handle_service_errors("getting node")
    def get_node(self, node_id: str) -> NodeDTO:
        node = self.nodes_gateway.get(node_id)
        return node_dto_from_domain(node)

    @handle_service_errors("deleting node")
    def delete_node(self, node_id: str) -> str:
        return self.nodes_gateway.delete(node_id)

    @handle_service_errors("importing ssh node")
    def import_ssh_node(self, node_import_request: NodesImportSSHRequestDTO) -> NodeDTO:
        import_ssh_params: NodeImportSshParams = NodeImportSshParams(
            hostname=node_import_request.hostname,
            endpoint=node_import_request.endpoint,
            username=node_import_request.username,
            ssh_key_id=node_import_request.ssh_key_id,
        )
        node: BaseNode = self.nodes_gateway.import_ssh(import_ssh_params)
        return node_dto_from_domain(node)

    @handle_service_errors("importing ssh nodes")
    def import_ssh_nodes(
        self, node_import_requests: List[NodesImportSSHRequestDTO]
    ) -> List[NodeDTO]:
        if len(node_import_requests) == 0:
            raise ServiceError(
                message="SSH import request must contain at least one node to import"
            )
        return [
            self.import_ssh_node(node_import_request)
            for node_import_request in node_import_requests
        ]

    @handle_service_errors("importing nodes from offer")
    def import_from_offer(self, dto: NodesImportFromOfferRequestDTO) -> List[NodeDTO]:
        import_from_offer_params: ImportFromOfferParams = ImportFromOfferParams(
            hostname=dto.hostname,
            offer_id=dto.offer_id,
            amount=dto.amount,
        )
        nodes = self.nodes_gateway.import_from_offer(import_from_offer_params)
        return [node_dto_from_domain(node) for node in nodes]


def get_node_service(config: AppConfig, access_token: str) -> NodeService:
    gateway_factory: GatewayFactory = GatewayFactory(config=config)
    nodes_gateway: NodesGateway = gateway_factory.create_nodes_gateway(
        access_token=access_token
    )
    return NodeService(nodes_gateway)

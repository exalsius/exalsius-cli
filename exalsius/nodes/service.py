from typing import List

from exalsius.config import AppConfig
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.nodes.domain import (
    ImportFromOfferParams,
    ImportSshParams,
    NodeFilterParams,
)
from exalsius.nodes.dtos import (
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    node_dto_from_domain,
)
from exalsius.nodes.gateway.base import NodesGateway


class NodeService:
    def __init__(self, nodes_gateway: NodesGateway):
        self.nodes_gateway: NodesGateway = nodes_gateway

    @handle_service_errors("listing nodes")
    def list_nodes(self, request: NodesListRequestDTO) -> List[NodeDTO]:
        node_filter_params: NodeFilterParams = NodeFilterParams(
            node_type=request.domain_node_type,
            provider=request.provider,
        )
        nodes = self.nodes_gateway.list(node_filter_params)
        return [node_dto_from_domain(node) for node in nodes]

    @handle_service_errors("getting node")
    def get_node(self, node_id: str) -> NodeDTO:
        node = self.nodes_gateway.get(node_id)
        return node_dto_from_domain(node)

    @handle_service_errors("deleting node")
    def delete_node(self, node_id: str) -> str:
        return self.nodes_gateway.delete(node_id)

    @handle_service_errors("importing ssh node")
    def import_ssh_node(self, dto: NodesImportSSHRequestDTO) -> NodeDTO:
        import_ssh_params: ImportSshParams = ImportSshParams(
            hostname=dto.hostname,
            endpoint=dto.endpoint,
            username=dto.username,
            ssh_key_id=dto.ssh_key_id,
        )
        node = self.nodes_gateway.import_ssh(import_ssh_params)
        return node_dto_from_domain(node)

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
    gateway_factory = GatewayFactory(config, access_token)
    nodes_gateway = gateway_factory.create_nodes_gateway()
    return NodeService(nodes_gateway)

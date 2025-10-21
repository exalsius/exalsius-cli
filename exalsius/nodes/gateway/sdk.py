from typing import List

from exalsius_api_client.api.nodes_api import NodesApi

from exalsius.nodes.domain import (
    BaseNode,
    ImportFromOfferParams,
    ImportSshParams,
    NodeFilterParams,
)
from exalsius.nodes.gateway.base import NodesGateway
from exalsius.nodes.gateway.commands import (
    DeleteNodeSdkCommand,
    GetNodeSdkCommand,
    ImportFromOfferSdkCommand,
    ImportSSHNodeSdkCommand,
    ListNodesSdkCommand,
)


class NodesGatewaySdk(NodesGateway):
    def __init__(self, nodes_api: NodesApi):
        self._nodes_api = nodes_api

    def list(self, node_filter_params: NodeFilterParams) -> List[BaseNode]:
        command = ListNodesSdkCommand(
            self._nodes_api,
            NodeFilterParams(
                node_type=node_filter_params.node_type,
                provider=node_filter_params.provider,
            ),
        )
        response: List[BaseNode] = command.execute()
        return response

    def get(self, node_id: str) -> BaseNode:
        command = GetNodeSdkCommand(self._nodes_api, node_id)
        response: BaseNode = command.execute()
        return response

    def delete(self, node_id: str) -> str:
        command = DeleteNodeSdkCommand(self._nodes_api, node_id)
        response: str = command.execute()
        return response

    def import_ssh(self, import_ssh_params: ImportSshParams) -> BaseNode:
        cmd_node_import_ssh: ImportSSHNodeSdkCommand = ImportSSHNodeSdkCommand(
            self._nodes_api,
            ImportSshParams(
                hostname=import_ssh_params.hostname,
                endpoint=import_ssh_params.endpoint,
                username=import_ssh_params.username,
                ssh_key_id=import_ssh_params.ssh_key_id,
            ),
        )
        node_id: str = cmd_node_import_ssh.execute()

        cmd_node_get: GetNodeSdkCommand = GetNodeSdkCommand(
            self._nodes_api,
            node_id,
        )
        response: BaseNode = cmd_node_get.execute()

        return response

    def import_from_offer(
        self, import_from_offer_params: ImportFromOfferParams
    ) -> List[BaseNode]:
        cmd_offer_import: ImportFromOfferSdkCommand = ImportFromOfferSdkCommand(
            self._nodes_api,
            ImportFromOfferParams(
                hostname=import_from_offer_params.hostname,
                offer_id=import_from_offer_params.offer_id,
                amount=import_from_offer_params.amount,
            ),
        )
        node_ids: List[str] = cmd_offer_import.execute()

        # TODO: this is an N+1 performance bottleneck; needs to be done in parallel or in a single API call
        nodes: List[BaseNode] = []
        for node_id in node_ids:
            cmd_node_get: GetNodeSdkCommand = GetNodeSdkCommand(
                self._nodes_api,
                node_id,
            )
            nodes.append(cmd_node_get.execute())

        return nodes

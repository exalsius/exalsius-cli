from typing import List

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import (
    NodeImportSshRequest as SdkNodeImportSshRequest,
)
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exls.nodes.adapters.gateway.commands import (
    DeleteNodeSdkCommand,
    GetNodeSdkCommand,
    ImportCloudNodeSdkCommand,
    ImportSSHNodeSdkCommand,
    ListNodesSdkCommand,
)
from exls.nodes.adapters.gateway.mappers import node_domain_from_sdk_model
from exls.nodes.core.domain import (
    BaseNode,
)
from exls.nodes.core.ports.gateway import (
    ImportCloudNodeParameters,
    ImportSelfmanagedNodeParameters,
    INodesGateway,
)
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.gateway.sdk.command import UnexpectedSdkCommandResponseError
from exls.shared.adapters.gateway.sdk.service import create_api_client


class NodesGatewaySdk(INodesGateway):
    def __init__(self, nodes_api: NodesApi):
        self._nodes_api = nodes_api

    def list(self, filter: NodesFilterCriteria) -> List[BaseNode]:
        command = ListNodesSdkCommand(
            self._nodes_api,
            request=filter,
        )
        response: NodesListResponse = command.execute()
        nodes: List[BaseNode] = [
            node_domain_from_sdk_model(node.actual_instance)
            for node in response.nodes
            if node.actual_instance is not None
        ]
        if filter.status is not None:
            nodes = [
                node
                for node in nodes
                if node.node_status.lower() == filter.status.lower()
            ]

        return nodes

    def get(self, node_id: str) -> BaseNode:
        command = GetNodeSdkCommand(self._nodes_api, node_id)
        response: NodeResponse = command.execute()
        if response.actual_instance is None:
            raise UnexpectedSdkCommandResponseError(
                message=f"Response for node {node_id} contains no actual instance. This is unexpected.",
                sdk_command=self.__class__.__name__,
            )
        return node_domain_from_sdk_model(response.actual_instance)

    def delete(self, node_id: str) -> str:
        command = DeleteNodeSdkCommand(self._nodes_api, node_id)
        response: NodeDeleteResponse = command.execute()
        return response.node_id

    def import_selfmanaged_node(self, request: ImportSelfmanagedNodeParameters) -> str:
        sdk_request: SdkNodeImportSshRequest = SdkNodeImportSshRequest(
            hostname=request.hostname,
            endpoint=request.endpoint,
            username=request.username,
            ssh_key_id=request.ssh_key_id,
        )
        cmd_node_import_ssh: ImportSSHNodeSdkCommand = ImportSSHNodeSdkCommand(
            self._nodes_api,
            request=sdk_request,
        )
        node_id: str = cmd_node_import_ssh.execute()
        return node_id

    def import_cloud_nodes(self, request: ImportCloudNodeParameters) -> List[str]:
        cmd_cloud_node_import: ImportCloudNodeSdkCommand = ImportCloudNodeSdkCommand(
            self._nodes_api,
            request=ImportCloudNodeRequest(
                hostname=request.hostname,
                offer_id=request.offer_id,
                amount=request.amount,
            ),
        )
        response: NodeImportResponse = cmd_cloud_node_import.execute()
        node_ids: List[str] = [node_id for node_id in response.node_ids]
        return node_ids


def create_nodes_gateway(backend_host: str, access_token: str) -> INodesGateway:
    nodes_api: NodesApi = NodesApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return NodesGatewaySdk(nodes_api=nodes_api)

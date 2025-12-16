from typing import List, Optional

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import (
    NodeImportSshRequest as SdkNodeImportSshRequest,
)
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exls.nodes.adapters.gateway.gateway import NodesGateway
from exls.nodes.adapters.gateway.sdk.commands import (
    DeleteNodeSdkCommand,
    GetNodeSdkCommand,
    ImportCloudNodeSdkCommand,
    ImportSSHNodeSdkCommand,
    ListNodesSdkCommand,
)
from exls.nodes.adapters.gateway.sdk.mappers import node_domain_from_sdk_model
from exls.nodes.core.domain import (
    BaseNode,
)
from exls.nodes.core.ports.operations import (
    ImportSelfmanagedNodeParameters,
)
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.gateway.sdk.command import UnexpectedSdkCommandResponseError


class SdkNodesGateway(NodesGateway):
    def __init__(self, nodes_api: NodesApi):
        self._nodes_api = nodes_api

    def list(self, filter: Optional[NodesFilterCriteria]) -> List[BaseNode]:
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
        if filter and filter.status is not None:
            nodes = [
                node for node in nodes if node.status.lower() == filter.status.lower()
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

    def import_selfmanaged_node(
        self, parameters: ImportSelfmanagedNodeParameters
    ) -> str:
        sdk_request: SdkNodeImportSshRequest = SdkNodeImportSshRequest(
            hostname=parameters.hostname,
            endpoint=parameters.endpoint,
            username=parameters.username,
            ssh_key_id=parameters.ssh_key_id,
        )
        cmd_node_import_ssh: ImportSSHNodeSdkCommand = ImportSSHNodeSdkCommand(
            self._nodes_api,
            request=sdk_request,
        )
        node_id: str = cmd_node_import_ssh.execute()
        return node_id

    def import_cloud_nodes(self, parameters: ImportCloudNodeRequest) -> List[str]:
        cmd_cloud_node_import: ImportCloudNodeSdkCommand = ImportCloudNodeSdkCommand(
            self._nodes_api,
            request=ImportCloudNodeRequest(
                hostname=parameters.hostname,
                offer_id=parameters.offer_id,
                amount=parameters.amount,
            ),
        )
        response: NodeImportResponse = cmd_cloud_node_import.execute()
        node_ids: List[str] = [node_id for node_id in response.node_ids]
        return node_ids

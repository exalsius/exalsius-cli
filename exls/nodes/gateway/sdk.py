from typing import List, Union

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)

from exls.core.commons.gateways.commands.sdk import UnexpectedSdkCommandResponseError
from exls.nodes.domain import (
    BaseNode,
    CloudNode,
    SelfManagedNode,
)
from exls.nodes.gateway.base import NodesGateway
from exls.nodes.gateway.commands import (
    DeleteNodeSdkCommand,
    GetNodeSdkCommand,
    ImportFromOfferSdkCommand,
    ImportSSHNodeSdkCommand,
    ListNodesSdkCommand,
)
from exls.nodes.gateway.dtos import (
    ImportFromOfferParams,
    NodeFilterParams,
    NodeImportSshParams,
)


class NodesGatewaySdk(NodesGateway):
    def __init__(self, nodes_api: NodesApi):
        self._nodes_api = nodes_api

    def _create_from_sdk_model(
        self,
        sdk_model: Union[SdkCloudNode, SdkSelfManagedNode],
    ) -> BaseNode:
        """Factory method to create a domain object from a SDK model."""

        if isinstance(sdk_model, SdkCloudNode):
            return CloudNode(sdk_model=sdk_model)
        return SelfManagedNode(sdk_model=sdk_model)

    def list(self, node_filter_params: NodeFilterParams) -> List[BaseNode]:
        command = ListNodesSdkCommand(
            self._nodes_api,
            params=node_filter_params,
        )
        response: NodesListResponse = command.execute()
        nodes: List[BaseNode] = [
            self._create_from_sdk_model(sdk_model=node.actual_instance)
            for node in response.nodes
            if node.actual_instance is not None
        ]

        if node_filter_params.status is not None:
            nodes = [
                node
                for node in nodes
                if node.node_status.lower() == node_filter_params.status.lower()
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
        return self._create_from_sdk_model(sdk_model=response.actual_instance)

    def delete(self, node_id: str) -> str:
        command = DeleteNodeSdkCommand(self._nodes_api, node_id)
        response: NodeDeleteResponse = command.execute()
        return response.node_id

    def import_ssh(self, import_ssh_params: NodeImportSshParams) -> BaseNode:
        cmd_node_import_ssh: ImportSSHNodeSdkCommand = ImportSSHNodeSdkCommand(
            self._nodes_api,
            params=import_ssh_params.to_sdk_request(),
        )
        node_id: str = cmd_node_import_ssh.execute()

        cmd_node_get: GetNodeSdkCommand = GetNodeSdkCommand(
            self._nodes_api,
            node_id,
        )
        response: NodeResponse = cmd_node_get.execute()
        if response.actual_instance is None:
            raise UnexpectedSdkCommandResponseError(
                message=f"Response for node {node_id} contains no actual instance. This is unexpected.",
                sdk_command=self.__class__.__name__,
            )
        return self._create_from_sdk_model(sdk_model=response.actual_instance)

    def import_from_offer(
        self, import_from_offer_params: ImportFromOfferParams
    ) -> List[BaseNode]:
        cmd_offer_import: ImportFromOfferSdkCommand = ImportFromOfferSdkCommand(
            self._nodes_api,
            params=import_from_offer_params,
        )
        node_ids: List[str] = cmd_offer_import.execute()

        # TODO: this is an N+1 performance bottleneck; needs to be done in parallel or in a single API call
        nodes: List[BaseNode] = []
        for node_id in node_ids:
            cmd_node_get: GetNodeSdkCommand = GetNodeSdkCommand(
                self._nodes_api,
                node_id,
            )
            response: NodeResponse = cmd_node_get.execute()
            if response.actual_instance is None:
                raise UnexpectedSdkCommandResponseError(
                    message=f"Response for node {node_id} contains no actual instance. This is unexpected.",
                    sdk_command=self.__class__.__name__,
                )
            nodes.append(
                self._create_from_sdk_model(sdk_model=response.actual_instance)
            )

        return nodes

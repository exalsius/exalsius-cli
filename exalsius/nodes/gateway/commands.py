from typing import List, Optional, Union

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)

from exalsius.core.commons.commands.sdk import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)
from exalsius.nodes.domain import (
    BaseNode,
    CloudNode,
    ImportFromOfferParams,
    ImportSshParams,
    NodeFilterParams,
    SelfManagedNode,
)


def _create_from_sdk_model(
    sdk_model: Union[SdkCloudNode, SdkSelfManagedNode],
) -> BaseNode:
    """Factory method to create a domain object from a SDK model."""

    if isinstance(sdk_model, SdkCloudNode):
        return CloudNode(sdk_model=sdk_model)
    else:
        return SelfManagedNode(sdk_model=sdk_model)


class BaseNodesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[NodesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all nodes commands. Fixes the generic API type to NodesApi."""

    pass


class ListNodesSdkCommand(BaseNodesSdkCommand[NodeFilterParams, List[BaseNode]]):
    """Command to list nodes."""

    def _execute_api_call(self, params: Optional[NodeFilterParams]) -> List[BaseNode]:
        assert params is not None
        response: NodesListResponse = self.api_client.list_nodes(
            node_type=params.node_type, provider=params.provider
        )
        return [
            _create_from_sdk_model(node_response.actual_instance)
            for node_response in response.nodes
            if node_response.actual_instance is not None
        ]


class GetNodeSdkCommand(BaseNodesSdkCommand[str, BaseNode]):
    """Command to get a node."""

    def _execute_api_call(self, params: Optional[str]) -> BaseNode:
        assert params is not None
        response: NodeResponse = self.api_client.describe_node(node_id=params)
        if response.actual_instance is None:
            raise UnexpectedSdkCommandResponseError(
                message=f"Response for node {params} contains no actual instance. This is unexpected.",
                sdk_command=self.__class__.__name__,
            )
        return _create_from_sdk_model(response.actual_instance)


class DeleteNodeSdkCommand(BaseNodesSdkCommand[str, str]):
    def _execute_api_call(self, params: Optional[str]) -> str:
        assert params is not None
        response: NodeDeleteResponse = self.api_client.delete_node(node_id=params)
        return response.node_id


class ImportSSHNodeSdkCommand(BaseNodesSdkCommand[ImportSshParams, str]):
    def _execute_api_call(self, params: Optional[ImportSshParams]) -> str:
        assert params is not None
        response: NodeImportResponse = self.api_client.import_ssh(
            NodeImportSshRequest(
                hostname=params.hostname,
                endpoint=params.endpoint,
                username=params.username,
                ssh_key_id=params.ssh_key_id,
            )
        )

        # validate response
        if len(response.node_ids) != 1:
            err_msg: str = ""
            if len(response.node_ids) == 0:
                err_msg = "no node IDs found"
            else:
                err_msg = "more than one node ID found"

            raise UnexpectedSdkCommandResponseError(
                message=f"Response for import SSH node contains {err_msg}. This is unexpected.",
                sdk_command=self.__class__.__name__,
                retryable=False,  # TODO: This should be possible but needs idempotency at backend
            )

        # we expect exactly one node ID
        return response.node_ids[0]


class ImportFromOfferSdkCommand(BaseNodesSdkCommand[ImportFromOfferParams, List[str]]):
    def _execute_api_call(self, params: Optional[ImportFromOfferParams]) -> List[str]:
        assert params is not None
        response: NodeImportResponse = self.api_client.import_node_from_offer(
            offer_id=params.offer_id,
            hostname=params.hostname,
            amount=params.amount,
        )

        # validate response
        if len(response.node_ids) == 0:
            raise UnexpectedSdkCommandResponseError(
                message="Response for import from offer contains no node IDs. This is unexpected.",
                sdk_command=self.__class__.__name__,
                retryable=False,  # TODO: This should be possible but needs idempotency at backend
            )

        return response.node_ids

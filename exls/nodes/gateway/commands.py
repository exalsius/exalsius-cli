from typing import List, Optional

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exls.core.commons.gateways.commands.sdk import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)
from exls.nodes.gateway.dtos import (
    ImportFromOfferParams,
    NodeFilterParams,
)


class BaseNodesSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[NodesApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all nodes commands. Fixes the generic API type to NodesApi."""

    pass


class ListNodesSdkCommand(BaseNodesSdkCommand[NodeFilterParams, NodesListResponse]):
    """Command to list nodes."""

    def _execute_api_call(
        self, params: Optional[NodeFilterParams]
    ) -> NodesListResponse:
        assert params is not None
        response: NodesListResponse = self.api_client.list_nodes(
            node_type=params.node_type, provider=params.provider
        )
        return response


class GetNodeSdkCommand(BaseNodesSdkCommand[str, NodeResponse]):
    """Command to get a node."""

    def _execute_api_call(self, params: Optional[str]) -> NodeResponse:
        assert params is not None
        response: NodeResponse = self.api_client.describe_node(node_id=params)
        if response.actual_instance is None:
            raise UnexpectedSdkCommandResponseError(
                message=f"Response for node {params} contains no actual instance. This is unexpected.",
                sdk_command=self.__class__.__name__,
            )
        return response


class DeleteNodeSdkCommand(BaseNodesSdkCommand[str, NodeDeleteResponse]):
    def _execute_api_call(self, params: Optional[str]) -> NodeDeleteResponse:
        assert params is not None
        response: NodeDeleteResponse = self.api_client.delete_node(node_id=params)
        return response


class ImportSSHNodeSdkCommand(BaseNodesSdkCommand[NodeImportSshRequest, str]):
    def _execute_api_call(self, params: Optional[NodeImportSshRequest]) -> str:
        assert params is not None
        response: NodeImportResponse = self.api_client.import_ssh(
            node_import_ssh_request=params
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

        return response.node_ids[0]


class ImportFromOfferSdkCommand(BaseNodesSdkCommand[ImportFromOfferParams, List[str]]):
    def _execute_api_call(self, params: Optional[ImportFromOfferParams]) -> List[str]:
        assert params is not None
        response: NodeImportResponse = self.api_client.import_node_from_offer(
            offer_id=params.offer_id,
            hostname=params.hostname,
            amount=params.amount,
        )
        if len(response.node_ids) == 0:
            raise UnexpectedSdkCommandResponseError(
                message="Response for import from offer contains no node IDs. This is unexpected.",
                sdk_command=self.__class__.__name__,
                retryable=False,
            )

        return response.node_ids

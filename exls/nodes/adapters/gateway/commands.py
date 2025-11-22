from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.gateway.sdk.command import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)


class BaseNodesSdkCommand[T_Cmd_Return](ExalsiusSdkCommand[NodesApi, T_Cmd_Return]):
    """Base class for all nodes commands. Fixes the generic API type to NodesApi."""

    pass


class ListNodesSdkCommand(BaseNodesSdkCommand[NodesListResponse]):
    """Command to list nodes."""

    def __init__(self, api_client: NodesApi, request: NodesFilterCriteria):
        super().__init__(api_client)

        self._request: NodesFilterCriteria = request

    def _execute_api_call(self) -> NodesListResponse:
        response: NodesListResponse = self.api_client.list_nodes(
            node_type=self._request.node_type, provider=self._request.provider
        )
        return response


class GetNodeSdkCommand(BaseNodesSdkCommand[NodeResponse]):
    """Command to get a node."""

    def __init__(self, api_client: NodesApi, node_id: str):
        super().__init__(api_client)

        self._node_id: str = node_id

    def _execute_api_call(self) -> NodeResponse:
        response: NodeResponse = self.api_client.describe_node(node_id=self._node_id)
        if response.actual_instance is None:
            raise UnexpectedSdkCommandResponseError(
                message=f"Response for node {self._node_id} contains no actual instance. This is unexpected.",
                sdk_command=self.__class__.__name__,
            )
        return response


class DeleteNodeSdkCommand(BaseNodesSdkCommand[NodeDeleteResponse]):
    def __init__(self, api_client: NodesApi, node_id: str):
        super().__init__(api_client)

        self._node_id: str = node_id

    def _execute_api_call(self) -> NodeDeleteResponse:
        response: NodeDeleteResponse = self.api_client.delete_node(
            node_id=self._node_id
        )
        return response


class ImportSSHNodeSdkCommand(BaseNodesSdkCommand[str]):
    def __init__(self, api_client: NodesApi, request: NodeImportSshRequest):
        super().__init__(api_client)

        self._request: NodeImportSshRequest = request

    def _execute_api_call(self) -> str:
        response: NodeImportResponse = self.api_client.import_ssh(
            node_import_ssh_request=self._request
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


class ImportCloudNodeSdkCommand(BaseNodesSdkCommand[NodeImportResponse]):
    def __init__(self, api_client: NodesApi, request: ImportCloudNodeRequest):
        super().__init__(api_client)

        self._request: ImportCloudNodeRequest = request

    def _execute_api_call(self) -> NodeImportResponse:
        response: NodeImportResponse = self.api_client.import_node_from_offer(
            offer_id=self._request.offer_id,
            hostname=self._request.hostname,
            amount=self._request.amount,
        )
        if len(response.node_ids) == 0:
            raise UnexpectedSdkCommandResponseError(
                message="Response for import from offer contains no node IDs. This is unexpected.",
                sdk_command=self.__class__.__name__,
                retryable=False,
            )

        return response

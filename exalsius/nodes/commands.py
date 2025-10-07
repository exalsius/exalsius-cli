from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exalsius.core.commons.commands.api import ExalsiusAPICommand
from exalsius.nodes.models import (
    NodesDeleteRequestDTO,
    NodesGetRequestDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
)


class ListNodesCommand(
    ExalsiusAPICommand[NodesApi, NodesListRequestDTO, NodesListResponse]
):
    def _execute_api_call(self) -> NodesListResponse:
        return self.api_client.list_nodes(self.request.node_type, self.request.provider)


class GetNodeCommand(ExalsiusAPICommand[NodesApi, NodesGetRequestDTO, NodeResponse]):
    def _execute_api_call(self) -> NodeResponse:
        return self.api_client.describe_node(self.request.node_id)


class DeleteNodeCommand(
    ExalsiusAPICommand[NodesApi, NodesDeleteRequestDTO, NodeDeleteResponse]
):
    def _execute_api_call(self) -> NodeDeleteResponse:
        return self.api_client.delete_node(self.request.node_id)


class ImportSSHNodeCommand(
    ExalsiusAPICommand[NodesApi, NodesImportSSHRequestDTO, NodeImportResponse]
):
    def _execute_api_call(self) -> NodeImportResponse:
        return self.api_client.import_ssh(
            NodeImportSshRequest(
                hostname=self.request.hostname,
                endpoint=self.request.endpoint,
                username=self.request.username,
                ssh_key_id=self.request.ssh_key_id,
            )
        )


class ImportFromOfferCommand(
    ExalsiusAPICommand[NodesApi, NodesImportFromOfferRequestDTO, NodeImportResponse]
):
    def _execute_api_call(self) -> NodeImportResponse:
        return self.api_client.import_node_from_offer(
            offer_id=self.request.offer_id,
            hostname=self.request.hostname,
            amount=self.request.amount,
        )

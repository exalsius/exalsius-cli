from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.nodes.models import (
    NodesDeleteRequestDTO,
    NodesGetRequestDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
)


class ListNodesCommand(BaseCommand):
    def __init__(
        self,
        request: NodesListRequestDTO,
    ):
        self.request: NodesListRequestDTO = request

    def execute(self) -> NodesListResponse:
        return self.request.api.list_nodes(
            self.request.node_type, self.request.provider
        )


class GetNodeCommand(BaseCommand):
    def __init__(
        self,
        request: NodesGetRequestDTO,
    ):
        self.request: NodesGetRequestDTO = request

    def execute(self) -> NodeResponse:
        return self.request.api.describe_node(self.request.node_id)


class DeleteNodeCommand(BaseCommand):
    def __init__(
        self,
        request: NodesDeleteRequestDTO,
    ):
        self.request: NodesDeleteRequestDTO = request

    def execute(self) -> NodeDeleteResponse:
        return self.request.api.delete_node(self.request.node_id)


class ImportSSHNodeCommand(BaseCommand):
    def __init__(
        self,
        request: NodesImportSSHRequestDTO,
    ):
        self.request: NodesImportSSHRequestDTO = request

    def execute(self) -> NodeImportResponse:
        return self.request.api.import_ssh(
            NodeImportSshRequest(
                hostname=self.request.hostname,
                endpoint=self.request.endpoint,
                username=self.request.username,
                ssh_key_id=self.request.ssh_key_id,
            )
        )


class ImportFromOfferCommand(BaseCommand):
    def __init__(
        self,
        request: NodesImportFromOfferRequestDTO,
    ):
        self.request: NodesImportFromOfferRequestDTO = request

    def execute(self) -> NodeImportResponse:
        return self.request.api.import_node_from_offer(
            offer_id=self.request.offer_id,
            hostname=self.request.hostname,
            amount=self.request.amount,
        )

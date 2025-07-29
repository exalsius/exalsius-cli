import base64

from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.nodes.models import (
    NodesDeleteRequestDTO,
    NodesGetRequestDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    SSHKeysAddRequestDTO,
    SSHKeysDeleteRequestDTO,
    SSHKeysDeleteResultDTO,
    SSHKeysListRequestDTO,
)


class ListNodesCommand(BaseCommand[NodesListResponse]):
    def __init__(
        self,
        request: NodesListRequestDTO,
    ):
        self.request: NodesListRequestDTO = request

    def execute(self) -> NodesListResponse:
        return self.request.api.list_nodes(
            self.request.node_type, self.request.provider
        )


class GetNodeCommand(BaseCommand[NodeResponse]):
    def __init__(
        self,
        request: NodesGetRequestDTO,
    ):
        self.request: NodesGetRequestDTO = request

    def execute(self) -> NodeResponse:
        return self.request.api.describe_node(self.request.node_id)


class DeleteNodeCommand(BaseCommand[NodeDeleteResponse]):
    def __init__(
        self,
        request: NodesDeleteRequestDTO,
    ):
        self.request: NodesDeleteRequestDTO = request

    def execute(self) -> NodeDeleteResponse:
        return self.request.api.delete_node(self.request.node_id)


class ImportSSHNodeCommand(BaseCommand[NodeImportResponse]):
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


class ImportFromOfferCommand(BaseCommand[NodeImportResponse]):
    def __init__(
        self,
        request: NodesImportFromOfferRequestDTO,
    ):
        self.request: NodesImportFromOfferRequestDTO = request

    def execute(self) -> NodeImportResponse:
        return self.request.api.import_node_from_offer(
            self.request.hostname,
            self.request.offer_id,
            self.request.amount,
        )


class ListSSHKeysCommand(BaseCommand[SshKeysListResponse]):
    def __init__(self, request: SSHKeysListRequestDTO):
        self.request: SSHKeysListRequestDTO = request

    def execute(self) -> SshKeysListResponse:
        return self.request.api.list_ssh_keys()


class AddSSHKeyCommand(BaseCommand[SshKeyCreateResponse]):
    def __init__(self, request: SSHKeysAddRequestDTO):
        self.request: SSHKeysAddRequestDTO = request

    def execute(self) -> SshKeyCreateResponse:
        return self.request.api.add_ssh_key(
            SshKeyCreateRequest(
                name=self.request.name,
                private_key_b64=base64.b64encode(
                    self.request.key_path.encode()
                ).decode(),
            )
        )


class DeleteSSHKeyCommand(BaseCommand[SSHKeysDeleteResultDTO]):
    def __init__(self, request: SSHKeysDeleteRequestDTO):
        self.request: SSHKeysDeleteRequestDTO = request

    def execute(self) -> SSHKeysDeleteResultDTO:
        self.request.api.delete_ssh_key(self.request.name)
        return SSHKeysDeleteResultDTO(success=True)

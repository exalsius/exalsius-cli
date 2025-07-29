import base64
from typing import Optional, Tuple, Union

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cloud_node import CloudNode
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.self_managed_node import SelfManagedNode
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse

from exalsius.base.operations import BaseOperation, BooleanOperation
from exalsius.clusters.models import CloudProvider
from exalsius.nodes.models import NodeType


class ListNodesOperation(BaseOperation[NodesListResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        node_type: Optional[NodeType],
        provider: Optional[CloudProvider],
    ):
        self.api_client = api_client
        self.node_type = node_type
        self.provider = provider

    def execute(self) -> Tuple[Optional[NodesListResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            nodes_list_response: NodesListResponse = api_instance.list_nodes(
                node_type=self.node_type,
                provider=self.provider,
            )
            return nodes_list_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"


class GetNodeOperation(BaseOperation[Union[CloudNode, SelfManagedNode]]):
    def __init__(
        self,
        api_client: ApiClient,
        node_id: str,
    ):
        self.api_client = api_client
        self.node_id = node_id

    def execute(self) -> Tuple[Optional[NodeResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            node_response: NodeResponse = api_instance.describe_node(self.node_id)
            return node_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"


class DeleteNodeOperation(BaseOperation[NodeDeleteResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        node_id: str,
    ):
        self.api_client = api_client
        self.node_id = node_id

    def execute(self) -> Tuple[Optional[NodeDeleteResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            node_delete_response: NodeDeleteResponse = api_instance.delete_node(
                self.node_id
            )
            return node_delete_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"


class ImportSSHNodeOperation(BaseOperation[NodeResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        hostname: str,
        endpoint: str,
        username: str,
        ssh_key_id: str,
    ):
        self.api_client = api_client
        self.hostname = hostname
        self.endpoint = endpoint
        self.username = username
        self.ssh_key_id = ssh_key_id

    def execute(self) -> Tuple[Optional[NodeImportResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        node_import_ssh_request = NodeImportSshRequest(
            hostname=self.hostname,
            endpoint=self.endpoint,
            username=self.username,
            ssh_key_id=self.ssh_key_id,
        )
        try:
            node_import_response: NodeImportResponse = api_instance.import_ssh(
                node_import_ssh_request
            )
            return node_import_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"


class ImportFromOfferOperation(BaseOperation[NodeImportResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        hostname: str,
        offer_id: str,
        amount: int,
    ):
        self.api_client = api_client
        self.hostname = hostname
        self.offer_id = offer_id
        self.amount = amount

    def execute(self) -> Tuple[Optional[NodeImportResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            node_import_response: NodeImportResponse = (
                api_instance.import_node_from_offer(
                    self.hostname,
                    self.offer_id,
                    self.amount,
                )
            )
            return node_import_response, None
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"


class ListSSHKeysOperation(BaseOperation[SshKeysListResponse]):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def execute(self) -> Tuple[Optional[SshKeysListResponse], Optional[str]]:
        api_instance = ManagementApi(self.api_client)
        try:
            ssh_keys_list_response: SshKeysListResponse = api_instance.list_ssh_keys()
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"
        return ssh_keys_list_response, None


class AddSSHKeyOperation(BaseOperation[SshKeyCreateResponse]):
    def __init__(self, api_client: ApiClient, name: str, key_path: str):
        self.api_client = api_client
        self.name = name
        self.key_path = key_path

    def execute(self) -> Tuple[Optional[SshKeyCreateResponse], Optional[str]]:
        api_instance = ManagementApi(self.api_client)

        with open(self.key_path, "r") as key_file:
            private_key = key_file.read()

        private_key_b64 = base64.b64encode(private_key.encode()).decode()

        try:
            ssh_key_create_request = SshKeyCreateRequest(
                name=self.name, private_key_b64=private_key_b64
            )
            ssh_key_create_response: SshKeyCreateResponse = api_instance.add_ssh_key(
                ssh_key_create_request
            )
        except ApiException as e:
            return None, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return None, f"unexpetced error: {str(e)}"

        return ssh_key_create_response, None


class DeleteSSHKeyOperation(BooleanOperation):
    def __init__(self, api_client: ApiClient, name: str):
        self.api_client = api_client
        self.name = name

    def execute(self) -> Tuple[bool, Optional[str]]:
        api_instance = ManagementApi(self.api_client)

        # we first have to find the ssh key by name
        # TODO: for this we should probably adjust or add an extra endpoint
        ssh_keys_list_response, error = ListSSHKeysOperation(self.api_client).execute()
        if error:
            return False, f"Failed to list SSH keys: {error}"
        if not ssh_keys_list_response:
            return False, "No SSH keys found"

        ssh_key_id = next(
            (
                key.id
                for key in ssh_keys_list_response.ssh_keys
                if key.name == self.name
            ),
            None,
        )
        if not ssh_key_id:
            return False, f"SSH key with name '{self.name}' not found"

        try:
            _ = api_instance.delete_ssh_key(ssh_key_id)
        except ApiException as e:
            return False, f"request failed with status code {e.status}: {str(e.body)}"
        except Exception as e:
            return False, f"unexpetced error: {str(e)}"
        return True, None

from typing import List, Optional, Tuple, Union

import exalsius_api_client
from exalsius_api_client import NodesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cloud_node import CloudNode
from exalsius_api_client.models.error import Error as ExalsiusError
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import NodeImportSshRequest
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.self_managed_node import SelfManagedNode

from exalsius.core.models.enums import CloudProvider, NodeType
from exalsius.core.operations.base import BaseOperation, ListOperation


class ListNodesOperation(ListOperation[BaseNode]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        node_type: NodeType,
        provider: CloudProvider,
    ):
        self.api_client = api_client
        self.node_type = node_type
        self.provider = provider

    def execute(self) -> Tuple[List[NodeResponse], Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            nodes_list_response: NodesListResponse = api_instance.list_nodes(
                node_type=self.node_type,
                provider=self.provider,
            )
            return nodes_list_response.nodes, None
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, str(e)


class GetNodeOperation(BaseOperation[Union[CloudNode, SelfManagedNode]]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        node_id: str,
    ):
        self.api_client = api_client
        self.node_id = node_id

    def execute(self) -> Tuple[NodeResponse, Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            node_response: NodeResponse = api_instance.describe_node(self.node_id)
            return node_response, None
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, str(e)


class DeleteNodeOperation(BaseOperation[NodeDeleteResponse]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        node_id: str,
    ):
        self.api_client = api_client
        self.node_id = node_id

    def execute(self) -> Tuple[NodeDeleteResponse, Optional[str]]:
        api_instance = NodesApi(self.api_client)
        try:
            node_delete_response: NodeDeleteResponse = api_instance.delete_node(
                self.node_id
            )
            return node_delete_response, None
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"


class ImportSSHNodeOperation(BaseOperation[NodeResponse]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
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

    def execute(self) -> Tuple[NodeResponse, Optional[str]]:
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
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, str(e)


class ImportFromOfferOperation(BaseOperation[NodeImportResponse]):
    def __init__(
        self,
        api_client: exalsius_api_client.ApiClient,
        hostname: str,
        offer_id: str,
        amount: int,
    ):
        self.api_client = api_client
        self.hostname = hostname
        self.offer_id = offer_id
        self.amount = amount

    def execute(self) -> Tuple[NodeImportResponse, Optional[str]]:
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
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
        except Exception as e:
            return None, str(e)

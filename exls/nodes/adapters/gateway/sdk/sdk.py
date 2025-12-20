from functools import singledispatch
from typing import List, Optional, Union

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.node_delete_response import NodeDeleteResponse
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_import_ssh_request import (
    NodeImportSshRequest as SdkNodeImportSshRequest,
)
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)

from exls.nodes.adapters.gateway.gateway import NodesGateway
from exls.nodes.adapters.gateway.sdk.commands import (
    DeleteNodeSdkCommand,
    GetNodeSdkCommand,
    ImportCloudNodeSdkCommand,
    ImportSSHNodeSdkCommand,
    ListNodesSdkCommand,
)
from exls.nodes.core.domain import (
    BaseNode,
    CloudNode,
    NodeResources,
    NodeStatus,
    SelfManagedNode,
)
from exls.nodes.core.ports.operations import (
    ImportSelfmanagedNodeParameters,
)
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.sdk.command import UnexpectedSdkCommandResponseError


def _map_node_resources_from_sdk_model(
    sdk_model: Union[SdkCloudNode, SdkSelfManagedNode],
) -> NodeResources:
    node_resources: NodeResources
    if sdk_model.hardware:
        node_resources = NodeResources(
            gpu_type=sdk_model.hardware.gpu_type or "unknown",
            gpu_vendor=sdk_model.hardware.gpu_vendor or "unknown",
            gpu_count=sdk_model.hardware.gpu_count or 0,
            cpu_cores=sdk_model.hardware.cpu_cores or 0,
            memory_gb=sdk_model.hardware.memory_gb or 0,
            storage_gb=sdk_model.hardware.storage_gb or 0,
        )
    else:
        node_resources = NodeResources(
            gpu_type="unknown",
            gpu_vendor="unknown",
            gpu_count=0,
            cpu_cores=0,
            memory_gb=0,
            storage_gb=0,
        )
    return node_resources


# singledispatch transforms a regular function into a generic function
# which can have multiple different implementations, and the one that
# gets called depends on the type of the first argument passed to it.
@singledispatch
def _node_domain_from_sdk_model(
    sdk_model: Union[SdkCloudNode, SdkSelfManagedNode],
) -> BaseNode:
    """Helper function to convert a SDK model to a domain node."""
    raise ValueError(f"Unknown node type: {type(sdk_model)}")


@_node_domain_from_sdk_model.register(SdkCloudNode)
def _(sdk_model: SdkCloudNode) -> CloudNode:
    """Helper function to convert a cloud SDK model to a domain node."""
    return CloudNode(
        id=sdk_model.id,
        hostname=sdk_model.hostname or "",
        import_time=sdk_model.import_time or None,
        status=NodeStatus.from_str(sdk_model.node_status),
        provider=sdk_model.provider,
        instance_type=sdk_model.instance_type,
        price_per_hour=f"{float(sdk_model.price_per_hour):.2f}",
        resources=_map_node_resources_from_sdk_model(sdk_model),
    )


@_node_domain_from_sdk_model.register(SdkSelfManagedNode)
def _(sdk_model: SdkSelfManagedNode) -> SelfManagedNode:
    """Helper function to convert a self-managed SDK model to a domain node."""
    return SelfManagedNode(
        id=sdk_model.id,
        hostname=sdk_model.hostname or "",
        import_time=sdk_model.import_time,
        status=NodeStatus.from_str(sdk_model.node_status),
        endpoint=sdk_model.endpoint,
        ssh_key_id=sdk_model.ssh_key_id,
        username=sdk_model.username,
        resources=_map_node_resources_from_sdk_model(sdk_model),
    )


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
            _node_domain_from_sdk_model(node.actual_instance)
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
        return _node_domain_from_sdk_model(response.actual_instance)

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

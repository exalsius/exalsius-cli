from functools import singledispatch
from typing import Union

from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)

from exls.nodes.core.domain import (
    BaseNode,
    CloudNode,
    NodeResources,
    NodeStatus,
    SelfManagedNode,
)


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
def node_domain_from_sdk_model(
    sdk_model: Union[SdkCloudNode, SdkSelfManagedNode],
) -> BaseNode:
    """Helper function to convert a SDK model to a domain node."""
    raise ValueError(f"Unknown node type: {type(sdk_model)}")


@node_domain_from_sdk_model.register(SdkCloudNode)
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


@node_domain_from_sdk_model.register(SdkSelfManagedNode)
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

from functools import singledispatch
from typing import Union

from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)

from exls.nodes.core.domain import BaseNode, CloudNode, NodeStatus, SelfManagedNode


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
    )

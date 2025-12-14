from typing import Any, Dict, Optional, Type, cast

from pydantic import BaseModel

from exls.clusters.adapters.ui.dtos import (
    AddNodesRequestDTO,
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    ClusterWithNodesDTO,
    DeployClusterRequestFromFlowDTO,
    NodeValidationIssueDTO,
    UnassignedClusterNodeDTO,
)
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext

DEFAULT_CLUSTER_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "updated_at": TableRenderContext.get_column("Updated At"),
}

# TODO: Refactor this to use a proper formatter function
DEFAULT_CLUSTER_WITH_NODES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "updated_at": TableRenderContext.get_column("Updated At"),
    "worker_nodes": TableRenderContext.get_column(
        "Worker Nodes",
        value_formatter=lambda nodes: ", ".join(
            [
                (
                    node.hostname
                    if isinstance(node, ClusterNodeDTO)
                    else (
                        str(cast(str, node["hostname"]))
                        if isinstance(node, dict)
                        else str(node)
                    )
                )
                for node in nodes
            ]
        ),
    ),
}

DEFAULT_NODE_VALIDATION_ISSUE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "node_id": TableRenderContext.get_column("Node ID", no_wrap=True),
    "node_spec_repr": TableRenderContext.get_column("Node Spec"),
    "reason": TableRenderContext.get_column("Error Message"),
}

DEFAULT_CLUSTER_NODE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("Node ID", no_wrap=True),
    "cluster_name": TableRenderContext.get_column("Cluster Name"),
    "hostname": TableRenderContext.get_column("Node Name"),
    "role": TableRenderContext.get_column("Node Role"),
    "status": TableRenderContext.get_column("Node Status"),
}

DEFAULT_CLUSTER_NODE_RESOURCES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "cluster_node.hostname": TableRenderContext.get_column("Node Name"),
    "free_resources.gpu_vendor": TableRenderContext.get_column("GPU Vendor"),
    "free_resources.gpu_type": TableRenderContext.get_column("GPU Type"),
    "free_resources.gpu_count": TableRenderContext.get_column("GPU Count"),
    "free_resources.cpu_cores": TableRenderContext.get_column("CPU Cores"),
    "free_resources.memory_gb": TableRenderContext.get_column("Memory GB"),
    "free_resources.storage_gb": TableRenderContext.get_column("Storage GB"),
}

DEFAULT_DEPLOY_CLUSTER_REQUEST_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "cluster_type": TableRenderContext.get_column("Cluster Type"),
    "gpu_type": TableRenderContext.get_column("GPU Type"),
    "enable_multinode_training": TableRenderContext.get_column(
        "Multinode Training Enabled"
    ),
    "enable_vpn": TableRenderContext.get_column("VPN Enabled"),
    # "enable_telemetry": TableRenderContext.get_column("Telemetry Enabled"),
    "worker_node_ids": TableRenderContext.get_column(
        "Worker Node IDs",
        value_formatter=lambda nodes: ", ".join(
            [
                (
                    node.name
                    if isinstance(node, UnassignedClusterNodeDTO)
                    else (
                        str(cast(str, node["name"]))
                        if isinstance(node, dict)
                        else str(node)
                    )
                )
                for node in nodes
            ]
        ),
    ),
}

DEFAULT_ADD_NODES_REQUEST_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "cluster_id": TableRenderContext.get_column("Cluster ID", no_wrap=True),
    "node_ids": TableRenderContext.get_column("Node IDs"),
}


DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    ClusterDTO: DEFAULT_CLUSTER_COLUMNS_RENDERING_MAP,
    ClusterNodeDTO: DEFAULT_CLUSTER_NODE_COLUMNS_RENDERING_MAP,
    ClusterWithNodesDTO: DEFAULT_CLUSTER_WITH_NODES_COLUMNS_RENDERING_MAP,
    ClusterNodeResourcesDTO: DEFAULT_CLUSTER_NODE_RESOURCES_COLUMNS_RENDERING_MAP,
    NodeValidationIssueDTO: DEFAULT_NODE_VALIDATION_ISSUE_COLUMNS_RENDERING_MAP,
    DeployClusterRequestFromFlowDTO: DEFAULT_DEPLOY_CLUSTER_REQUEST_COLUMNS_RENDERING_MAP,
    AddNodesRequestDTO: DEFAULT_ADD_NODES_REQUEST_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)

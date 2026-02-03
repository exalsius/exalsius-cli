from typing import Dict, cast

from exls.clusters.adapters.ui.flows.cluster_deploy import FlowClusterNodeDTO
from exls.clusters.core.domain import ClusterNode
from exls.shared.adapters.ui.output.render.service import (
    format_datetime,
    format_datetime_humanized,
)
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

# -----------------------------------------------------------------------------
# CLUSTER LIST VIEWS (humanized timestamps)
# -----------------------------------------------------------------------------

_CLUSTER_LIST_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column(
        "Created At", value_formatter=format_datetime_humanized
    ),
    "updated_at": TableRenderContext.get_column(
        "Updated At", value_formatter=format_datetime_humanized
    ),
}

CLUSTER_LIST_VIEW = ViewContext.from_table_columns(_CLUSTER_LIST_COLUMNS)


_CLUSTER_WITH_NODES_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column(
        "Created At", value_formatter=format_datetime_humanized
    ),
    "updated_at": TableRenderContext.get_column(
        "Updated At", value_formatter=format_datetime_humanized
    ),
    "nodes": TableRenderContext.get_column(
        "Worker Nodes",
        value_formatter=lambda nodes: ", ".join(
            [
                (
                    node.hostname
                    if isinstance(node, ClusterNode)
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

CLUSTER_WITH_NODES_VIEW = ViewContext.from_table_columns(_CLUSTER_WITH_NODES_COLUMNS)


# -----------------------------------------------------------------------------
# CLUSTER DETAIL VIEWS (ISO timestamps for single resource get)
# -----------------------------------------------------------------------------

_CLUSTER_DETAIL_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column(
        "Created At", value_formatter=format_datetime
    ),
    "updated_at": TableRenderContext.get_column(
        "Updated At", value_formatter=format_datetime
    ),
}

CLUSTER_DETAIL_VIEW = ViewContext.from_table_columns(_CLUSTER_DETAIL_COLUMNS)


# -----------------------------------------------------------------------------
# NODE VIEWS
# -----------------------------------------------------------------------------

_CLUSTER_NODE_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("Node ID", no_wrap=True),
    "hostname": TableRenderContext.get_column("Node Name"),
    "role": TableRenderContext.get_column("Node Role"),
    "status": TableRenderContext.get_column("Node Status"),
}

CLUSTER_NODE_LIST_VIEW = ViewContext.from_table_columns(_CLUSTER_NODE_COLUMNS)


_CLUSTER_NODE_RESOURCES_COLUMNS: Dict[str, Column] = {
    "hostname": TableRenderContext.get_column("Node Name"),
    "free_resources.gpu_vendor": TableRenderContext.get_column("GPU Vendor"),
    "free_resources.gpu_type": TableRenderContext.get_column("GPU Type"),
    "free_resources.gpu_count": TableRenderContext.get_column("GPU Count"),
    "free_resources.cpu_cores": TableRenderContext.get_column("CPU Cores"),
    "free_resources.memory_gb": TableRenderContext.get_column("Memory GB"),
    "free_resources.storage_gb": TableRenderContext.get_column("Storage GB"),
}

CLUSTER_NODE_RESOURCES_VIEW = ViewContext.from_table_columns(
    _CLUSTER_NODE_RESOURCES_COLUMNS
)


# -----------------------------------------------------------------------------
# ISSUE VIEWS
# -----------------------------------------------------------------------------

_CLUSTER_NODE_ISSUE_COLUMNS: Dict[str, Column] = {
    "node.id": TableRenderContext.get_column("Node ID", no_wrap=True),
    "node.hostname": TableRenderContext.get_column("Node Name"),
    "error_message": TableRenderContext.get_column("Error Message"),
}

CLUSTER_NODE_ISSUE_VIEW = ViewContext.from_table_columns(_CLUSTER_NODE_ISSUE_COLUMNS)


# -----------------------------------------------------------------------------
# DTO VIEWS (Input/Flows)
# -----------------------------------------------------------------------------

_FLOW_DEPLOY_CLUSTER_REQUEST_COLUMNS: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "cluster_type": TableRenderContext.get_column("Cluster Type"),
    "gpu_type": TableRenderContext.get_column("GPU Type"),
    "enable_multinode_training": TableRenderContext.get_column(
        "Multinode Training Enabled"
    ),
    "prepare_llm_inference_environment": TableRenderContext.get_column(
        "LLM Inference Environment Prepared"
    ),
    "enable_vpn": TableRenderContext.get_column("VPN Enabled"),
    "worker_node_ids": TableRenderContext.get_column(
        "Worker Node IDs",
        value_formatter=lambda nodes: ", ".join(
            [
                (
                    node.name
                    if isinstance(node, FlowClusterNodeDTO)
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

FLOW_DEPLOY_CLUSTER_REQUEST_VIEW = ViewContext.from_table_columns(
    _FLOW_DEPLOY_CLUSTER_REQUEST_COLUMNS
)


_ADD_NODES_REQUEST_COLUMNS: Dict[str, Column] = {
    "cluster_id": TableRenderContext.get_column("Cluster ID", no_wrap=True),
    "node_ids": TableRenderContext.get_column("Node IDs"),
}

ADD_NODES_REQUEST_VIEW = ViewContext.from_table_columns(_ADD_NODES_REQUEST_COLUMNS)

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.shared.adapters.ui.output.render.service import format_na
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.workspaces.adapters.dtos import (
    MultiNodeWorkspaceDTO,
    SingleNodeWorkspaceDTO,
    WorkspaceDTO,
)
from exls.workspaces.adapters.ui.dtos import (
    DeployMultiNodeWorkspaceRequestDTO,
    DeploySingleNodeWorkspaceRequestDTO,
)

DEFAULT_SINGLE_WORKSPACE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "template_name": TableRenderContext.get_column("Template"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
}

DEFAULT_LIST_WORKSPACE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "template_name": TableRenderContext.get_column("Template"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
}

DEFAULT_SINGLE_NODE_WORKSPACE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "template_name": TableRenderContext.get_column("Template"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "access_information.endpoint": TableRenderContext.get_column(
        "Access Endpoint", value_formatter=format_na
    ),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
}

DEFAULT_MULTI_NODE_WORKSPACE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "template_name": TableRenderContext.get_column("Template"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column("Created At"),
    "total_nodes": TableRenderContext.get_column("Total GPUs"),
    "gpu_types": TableRenderContext.get_column("GPU Types"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
}

DEFAULT_DEPLOY_SINGLE_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP: Dict[
    str, Column
] = {
    "cluster_name": TableRenderContext.get_column("Cluster Name"),
    "workspace_name": TableRenderContext.get_column("Workspace Name"),
    "workspace_template_name": TableRenderContext.get_column("Workspace Template"),
    "num_gpus": TableRenderContext.get_column("Number of GPUs"),
    "variables": TableRenderContext.get_column("Variables"),
}

DEFAULT_DEPLOY_MULTI_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP: Dict[
    str, Column
] = {
    "cluster_name": TableRenderContext.get_column("Cluster Name"),
    "workspace_name": TableRenderContext.get_column("Workspace Name"),
    "workspace_template_name": TableRenderContext.get_column("Workspace Template"),
    "total_nodes": TableRenderContext.get_column("Total GPUs"),
    "gpu_types": TableRenderContext.get_column("GPU Types"),
    "variables": TableRenderContext.get_column("Variables"),
}


DTO_LIST_DATA_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    WorkspaceDTO: DEFAULT_LIST_WORKSPACE_COLUMNS_RENDERING_MAP,
    SingleNodeWorkspaceDTO: DEFAULT_SINGLE_NODE_WORKSPACE_COLUMNS_RENDERING_MAP,
    MultiNodeWorkspaceDTO: DEFAULT_MULTI_NODE_WORKSPACE_COLUMNS_RENDERING_MAP,
    DeploySingleNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_SINGLE_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
    DeployMultiNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_MULTI_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
}

DTO_SINGLE_DATA_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    WorkspaceDTO: DEFAULT_SINGLE_WORKSPACE_COLUMNS_RENDERING_MAP,
    SingleNodeWorkspaceDTO: DEFAULT_SINGLE_NODE_WORKSPACE_COLUMNS_RENDERING_MAP,
    MultiNodeWorkspaceDTO: DEFAULT_MULTI_NODE_WORKSPACE_COLUMNS_RENDERING_MAP,
    DeploySingleNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_SINGLE_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
    DeployMultiNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_MULTI_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(
    dto_type: Type[BaseModel], list_data: bool = False
) -> Optional[Dict[str, Column]]:
    if list_data:
        return DTO_LIST_DATA_DISPLAY_CONFIG_MAP.get(dto_type, None)
    else:
        return DTO_SINGLE_DATA_DISPLAY_CONFIG_MAP.get(dto_type, None)

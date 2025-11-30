from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.workspaces.adapters.dtos import WorkspaceDTO
from exls.workspaces.adapters.ui.dtos import (
    DeployMultiNodeWorkspaceRequestDTO,
    DeploySingleNodeWorkspaceRequestDTO,
)

DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_id": TableRenderContext.get_column("ID", no_wrap=True),
    "workspace_name": TableRenderContext.get_column("Name"),
    "workspace_template_name": TableRenderContext.get_column("Template"),
    "workspace_status": TableRenderContext.get_column("Status"),
    "workspace_created_at": TableRenderContext.get_column("Created At"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
    "workspace_access_information.access_endpoint": TableRenderContext.get_column(
        "Access Endpoint"
    ),
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


DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    WorkspaceDTO: DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP,
    DeploySingleNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_SINGLE_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
    DeployMultiNodeWorkspaceRequestDTO: DEFAULT_DEPLOY_MULTI_NODE_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)

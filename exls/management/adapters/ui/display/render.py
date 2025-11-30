from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.management.adapters.dtos import (
    ClusterTemplateDTO,
    CredentialsDTO,
    ImportSshKeyRequestDTO,
    ServiceTemplateDTO,
    SshKeyDTO,
    WorkspaceTemplateDTO,
)
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext

DEFAULT_CLUSTER_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "description": TableRenderContext.get_column("Description"),
    "k8s_version": TableRenderContext.get_column("Kubernetes Version"),
}

DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "description": TableRenderContext.get_column("Description"),
}

DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "description": TableRenderContext.get_column("Description"),
    "variables": TableRenderContext.get_column("Variables"),
}

DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
}

DEFAULT_ADD_SSH_KEY_REQUEST_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "key_path": TableRenderContext.get_column("Key Path"),
}

DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "description": TableRenderContext.get_column("Description"),
    "variables": TableRenderContext.get_column("Variables"),
}

DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    ClusterTemplateDTO: DEFAULT_CLUSTER_TEMPLATES_COLUMNS_RENDERING_MAP,
    CredentialsDTO: DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP,
    ServiceTemplateDTO: DEFAULT_SERVICE_TEMPLATES_COLUMNS_RENDERING_MAP,
    SshKeyDTO: DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP,
    ImportSshKeyRequestDTO: DEFAULT_ADD_SSH_KEY_REQUEST_COLUMNS_RENDERING_MAP,
    WorkspaceTemplateDTO: DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)

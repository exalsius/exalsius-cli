from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.management.adapters.ui.flows.import_ssh_key import FlowImportSshKeyRequestDTO
from exls.management.core.domain import (
    SshKey,
    WorkspaceTemplate,
)
from exls.shared.adapters.ui.output.render.service import format_short_id
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext

DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column(
        "ID", no_wrap=True, value_formatter=format_short_id
    ),
    "name": TableRenderContext.get_column("Name"),
    "scope": TableRenderContext.get_column("Scope"),
}

DEFAULT_ADD_SSH_KEY_REQUEST_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "key_path": TableRenderContext.get_column("Key Path"),
    "scope": TableRenderContext.get_column("Scope"),
}

DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": TableRenderContext.get_column("Name"),
    "description": TableRenderContext.get_column("Description"),
    "variables": TableRenderContext.get_column("Variables"),
}

DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    SshKey: DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP,
    FlowImportSshKeyRequestDTO: DEFAULT_ADD_SSH_KEY_REQUEST_COLUMNS_RENDERING_MAP,
    WorkspaceTemplate: DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DISPLAY_CONFIG_MAP.get(dto_type, None)

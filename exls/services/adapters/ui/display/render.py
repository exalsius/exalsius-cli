from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.services.adapters.dtos import ServiceDTO
from exls.shared.adapters.ui.display.render.table import Column, TableRenderContext

DEFAULT_SERVICES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "cluster_id": TableRenderContext.get_column("Cluster ID"),
    "service_template": TableRenderContext.get_column("Service Template"),
    "created_at": TableRenderContext.get_column("Created At"),
}

DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    ServiceDTO: DEFAULT_SERVICES_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)

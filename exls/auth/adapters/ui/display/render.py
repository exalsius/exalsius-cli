from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.auth.adapters.dtos import UserInfoDTO
from exls.shared.adapters.ui.display.render.table import Column, TableRenderContext

DEFAULT_USER_INFO_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "email": TableRenderContext.get_column("Email"),
    "nickname": TableRenderContext.get_column("Username"),
    "sub": TableRenderContext.get_column("Subject"),
}


DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    UserInfoDTO: DEFAULT_USER_INFO_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)

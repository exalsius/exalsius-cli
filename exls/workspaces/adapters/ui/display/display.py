from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.output.render.table import Column
from exls.workspaces.adapters.ui.display.render import get_columns_rendering_map


class IOWorkspacesFacade(IOBaseModelFacade):
    def get_columns_rendering_map(
        self, data_type: Type[BaseModel], list_data: bool = False
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(data_type, list_data)

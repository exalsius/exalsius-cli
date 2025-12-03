from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.nodes.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.output.render.table import (
    Column,
)


class IONodesFacade(IOBaseModelFacade):
    def get_columns_rendering_map(
        self, data_type: Type[BaseModel], list_data: bool = False
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(data_type)

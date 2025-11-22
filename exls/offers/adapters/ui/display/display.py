from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.offers.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.display.display import BaseModelInteractionManager
from exls.shared.adapters.ui.display.render.table import Column


class OffersInteractionManager(BaseModelInteractionManager):
    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(dto_type)

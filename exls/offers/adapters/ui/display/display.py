from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.offers.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.output.render.table import Column


class IOOffersFacade(IOBaseModelFacade):
    def get_columns_rendering_map(
        self, data_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(data_type)

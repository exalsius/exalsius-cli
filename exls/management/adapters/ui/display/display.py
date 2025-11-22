from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.management.adapters.ui.display.interfaces import IManagementInputManager
from exls.management.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.display import validators
from exls.shared.adapters.ui.display.display import BaseModelInteractionManager
from exls.shared.adapters.ui.display.render.table import Column


class ManagementInteractionManager(
    BaseModelInteractionManager, IManagementInputManager
):
    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(dto_type)

    def ask_ssh_key_name(self, default: Optional[str] = None) -> str:
        return self.input_manager.ask_text(
            "Enter SSH key name:",
            default=default,
            validator=validators.non_empty_string_validator,
        )

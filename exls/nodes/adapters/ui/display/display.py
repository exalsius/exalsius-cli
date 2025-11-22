from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.nodes.adapters.ui.display.interfaces import (
    INodesInputManager,
)
from exls.nodes.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.display import validators
from exls.shared.adapters.ui.display.display import BaseModelInteractionManager
from exls.shared.adapters.ui.display.render.table import (
    Column,
)


class NodesInteractionManager(BaseModelInteractionManager, INodesInputManager):
    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(dto_type)

    def ask_node_name(self, default: Optional[str] = None) -> str:
        return self.input_manager.ask_text(
            "Enter node name:",
            default=default,
            validator=validators.kubernetes_name_validator,
        )

    def ask_node_endpoint(self) -> str:
        return self.input_manager.ask_text(
            "Enter node endpoint (IPv4 address with optional port):",
            validator=validators.ipv4_address_validator,
        )

    def ask_node_username(self, default: Optional[str] = None) -> str:
        return self.input_manager.ask_text(
            "Enter node username:",
            default=default,
            validator=validators.non_empty_string_validator,
        )

from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.shared.adapters.ui.display import validators
from exls.shared.adapters.ui.display.display import BaseModelInteractionManager
from exls.shared.adapters.ui.display.render.table import Column
from exls.workspaces.adapters.ui.display.interface import IWorkspaceInputManager
from exls.workspaces.adapters.ui.display.render import get_columns_rendering_map


class WorkspacesInteractionManager(BaseModelInteractionManager, IWorkspaceInputManager):
    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(dto_type)

    def ask_workspace_name(self, default: Optional[str] = None) -> str:
        return self.input_manager.ask_text(
            "Enter workspace name:",
            default=default,
            validator=validators.kubernetes_name_validator,
        )

from typing import Dict, Optional, Type

from pydantic import BaseModel

from exls.clusters.adapters.ui.display.interface import IClusterInputManager
from exls.clusters.adapters.ui.display.render import get_columns_rendering_map
from exls.shared.adapters.ui.display import validators
from exls.shared.adapters.ui.display.display import BaseModelInteractionManager
from exls.shared.adapters.ui.display.render.table import Column


class ClustersInteractionManager(BaseModelInteractionManager, IClusterInputManager):
    def get_columns_rendering_map(
        self, dto_type: Type[BaseModel]
    ) -> Optional[Dict[str, Column]]:
        return get_columns_rendering_map(dto_type)

    def ask_cluster_name(self, default: Optional[str] = None) -> str:
        return self.input_manager.ask_text(
            "Enter cluster name:",
            default=default,
            validator=validators.kubernetes_name_validator,
        )

    def ask_cluster_type(self, default: Optional[str] = None) -> str:
        return "TODO"

    def ask_gpu_type(self, default: Optional[str] = None) -> str:
        return "TODO"

    def ask_enable_multinode_training(self, default: Optional[bool] = None) -> bool:
        return False

    def ask_enable_telemetry(self, default: Optional[bool] = None) -> bool:
        return False

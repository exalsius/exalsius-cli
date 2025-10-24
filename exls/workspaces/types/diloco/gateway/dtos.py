from typing import Any, Dict, Optional

from pydantic import PositiveInt, StrictStr

from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


class DeployDilocoWorkspaceParams(DeployWorkspaceParams):
    template_id: StrictStr = "diloco-training-template"
    nodes: PositiveInt
    ephemeral_storage_gb_per_node: Optional[PositiveInt]
    diloco_config: Dict[str, Any]

from typing import Optional

from pydantic import StrictStr

from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


class DeployMarimoWorkspaceParams(DeployWorkspaceParams):
    template_id: StrictStr = "marimo-workspace-template"
    docker_image: Optional[StrictStr] = None
    marimo_password: StrictStr

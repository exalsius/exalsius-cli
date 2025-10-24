from typing import Optional

from pydantic import StrictStr

from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


class DeployDevPodWorkspaceParams(DeployWorkspaceParams):
    template_id: StrictStr = "vscode-devcontainer-template"
    docker_image: Optional[StrictStr] = None

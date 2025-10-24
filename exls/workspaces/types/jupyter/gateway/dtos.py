from typing import Optional

from pydantic import StrictStr

from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


class DeployJupyterWorkspaceParams(DeployWorkspaceParams):
    template_id: StrictStr = "jupyter-notebook-template"
    docker_image: Optional[StrictStr] = None
    jupyter_password: StrictStr

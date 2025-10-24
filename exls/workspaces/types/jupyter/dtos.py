from typing import Optional

from pydantic import StrictStr

from exls.workspaces.common.dtos import DeployWorkspaceRequestDTO


class DeployJupyterWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = None
    jupyter_password: StrictStr

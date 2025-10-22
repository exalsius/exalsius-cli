from typing import Optional

from pydantic import StrictStr

from exalsius.workspaces.dtos import DeployWorkspaceRequestDTO


class DeployJupyterWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = None
    jupyter_password: StrictStr

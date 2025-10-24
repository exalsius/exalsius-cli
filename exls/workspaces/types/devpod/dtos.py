from typing import Optional

from pydantic import StrictStr

from exls.workspaces.common.dtos import DeployWorkspaceRequestDTO


class DeployDevPodWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = None

from typing import Optional

from pydantic import StrictStr

from exalsius.workspaces.dtos import DeployWorkspaceRequestDTO


class DeployDevPodWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = None

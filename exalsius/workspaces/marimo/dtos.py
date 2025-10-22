from typing import Optional

from pydantic import Field, StrictStr

from exalsius.workspaces.dtos import DeployWorkspaceRequestDTO


class DeployMarimoWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = Field(
        None, description="The docker image to use for the workspace"
    )
    marimo_password: str = Field(
        ..., description="The password for the Marimo Webinterface"
    )

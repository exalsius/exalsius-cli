from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import StrictStr

from exls.workspaces.common.domain import (
    DeployWorkspaceParams,
    ResourceRequested,
)
from exls.workspaces.types.jupyter.dtos import DeployJupyterWorkspaceRequestDTO


class DeployJupyterWorkspaceParams(DeployWorkspaceParams):
    template_id: str = ClassVar[str]("jupyter-notebook-template")
    docker_image: Optional[StrictStr] = None
    jupyter_password: StrictStr

    @classmethod
    def from_request_dto(
        cls, request_dto: DeployJupyterWorkspaceRequestDTO
    ) -> DeployJupyterWorkspaceParams:
        return DeployJupyterWorkspaceParams(
            cluster_id=request_dto.cluster_id,
            name=request_dto.name,
            resources=ResourceRequested.from_request_dto(request_dto.resources),
            description="Jupyter workspace",
            to_be_deleted_at=request_dto.to_be_deleted_at,
            docker_image=request_dto.docker_image,
            jupyter_password=request_dto.jupyter_password,
        )

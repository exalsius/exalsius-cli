from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import StrictStr

from exls.workspaces.common.domain import (
    DeployWorkspaceParams,
    ResourceRequested,
)
from exls.workspaces.types.devpod.dtos import DeployDevPodWorkspaceRequestDTO


class DeployDevPodWorkspaceParams(DeployWorkspaceParams):
    template_id: str = ClassVar[str]("vscode-devcontainer-template")
    docker_image: Optional[StrictStr] = None

    @classmethod
    def from_request_dto(
        cls, request_dto: DeployDevPodWorkspaceRequestDTO
    ) -> DeployDevPodWorkspaceParams:
        return DeployDevPodWorkspaceParams(
            cluster_id=request_dto.cluster_id,
            name=request_dto.name,
            resources=ResourceRequested.from_request_dto(request_dto.resources),
            description="DevPod workspace",
            to_be_deleted_at=request_dto.to_be_deleted_at,
        )

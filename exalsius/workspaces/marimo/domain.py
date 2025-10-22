from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import StrictStr

from exalsius.workspaces.domain import DeployWorkspaceParams, ResourceRequested
from exalsius.workspaces.marimo.dtos import DeployMarimoWorkspaceRequestDTO


class DeployMarimoWorkspaceParams(DeployWorkspaceParams):
    template_id: str = ClassVar[str]("marimo-workspace-template")
    docker_image: Optional[StrictStr] = None
    marimo_password: StrictStr

    @classmethod
    def from_request_dto(
        cls, request_dto: DeployMarimoWorkspaceRequestDTO
    ) -> DeployMarimoWorkspaceParams:
        return DeployMarimoWorkspaceParams(
            cluster_id=request_dto.cluster_id,
            name=request_dto.name,
            resources=ResourceRequested.from_request_dto(request_dto.resources),
            description="Marimo workspace",
            to_be_deleted_at=request_dto.to_be_deleted_at,
            docker_image=request_dto.docker_image,
            marimo_password=request_dto.marimo_password,
        )

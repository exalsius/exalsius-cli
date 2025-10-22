from __future__ import annotations

from typing import Any, ClassVar, Dict, Optional

from pydantic import PositiveInt

from exls.workspaces.common.domain import (
    DeployWorkspaceParams,
    ResourceRequested,
)
from exls.workspaces.types.diloco.dtos import DeployDilocoWorkspaceRequestDTO


class DeployDilocoWorkspaceParams(DeployWorkspaceParams):
    template_id: str = ClassVar[str]("diloco-training-template")
    nodes: PositiveInt
    ephemeral_storage_gb_per_node: Optional[PositiveInt]
    diloco_config: Dict[str, Any]

    @classmethod
    def from_request_dto(
        cls,
        request_dto: DeployDilocoWorkspaceRequestDTO,
        diloco_config_from_file: dict[str, Any],
    ) -> DeployDilocoWorkspaceParams:
        diloco_config: dict[str, Any] = {**diloco_config_from_file}
        if request_dto.wandb_user_key is not None:
            diloco_config["wandbUserKey"] = request_dto.wandb_user_key
        if request_dto.wandb_project_name is not None:
            diloco_config["wandbProjectName"] = request_dto.wandb_project_name
        if request_dto.wandb_group is not None:
            diloco_config["wandbGroup"] = request_dto.wandb_group
        if request_dto.huggingface_token is not None:
            diloco_config["huggingfaceToken"] = request_dto.huggingface_token

        return DeployDilocoWorkspaceParams(
            cluster_id=request_dto.cluster_id,
            name=request_dto.name,
            resources=ResourceRequested.from_request_dto(request_dto.resources),
            description="DiLoCo workspace",
            to_be_deleted_at=request_dto.to_be_deleted_at,
            nodes=request_dto.nodes,
            ephemeral_storage_gb_per_node=request_dto.resources.ephemeral_storage_gb,
            diloco_config=diloco_config,
        )

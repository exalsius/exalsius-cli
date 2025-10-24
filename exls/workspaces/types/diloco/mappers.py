from typing import Any, Dict

from exls.workspaces.common.mappers import requested_resources_params_from_request_dto
from exls.workspaces.types.diloco.dtos import DeployDilocoWorkspaceRequestDTO
from exls.workspaces.types.diloco.gateway.dtos import DeployDilocoWorkspaceParams


def deploy_diloco_workspace_params_from_request_dto(
    request_dto: DeployDilocoWorkspaceRequestDTO,
    diloco_config_from_file: Dict[str, Any],
) -> DeployDilocoWorkspaceParams:
    diloco_config: Dict[str, Any] = {**diloco_config_from_file}
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
        resources=requested_resources_params_from_request_dto(request_dto.resources),
        description="DiLoCo workspace",
        to_be_deleted_at=request_dto.to_be_deleted_at,
        nodes=request_dto.nodes,
        ephemeral_storage_gb_per_node=request_dto.resources.ephemeral_storage_gb,
        diloco_config=diloco_config,
    )

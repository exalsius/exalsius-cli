from exls.workspaces.common.mappers import requested_resources_params_from_request_dto
from exls.workspaces.types.devpod.dtos import DeployDevPodWorkspaceRequestDTO
from exls.workspaces.types.devpod.gateway.dtos import DeployDevPodWorkspaceParams


def deploy_devpod_workspace_params_from_request_dto(
    request_dto: DeployDevPodWorkspaceRequestDTO,
) -> DeployDevPodWorkspaceParams:
    return DeployDevPodWorkspaceParams(
        cluster_id=request_dto.cluster_id,
        name=request_dto.name,
        resources=requested_resources_params_from_request_dto(
            request_dto=request_dto.resources
        ),
        description="DevPod workspace",
        to_be_deleted_at=request_dto.to_be_deleted_at,
    )

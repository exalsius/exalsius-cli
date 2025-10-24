from exls.workspaces.common.mappers import requested_resources_params_from_request_dto
from exls.workspaces.types.marimo.dtos import DeployMarimoWorkspaceRequestDTO
from exls.workspaces.types.marimo.gateway.dtos import DeployMarimoWorkspaceParams


def deploy_marimo_workspace_params_from_request_dto(
    request_dto: DeployMarimoWorkspaceRequestDTO,
) -> DeployMarimoWorkspaceParams:
    return DeployMarimoWorkspaceParams(
        cluster_id=request_dto.cluster_id,
        name=request_dto.name,
        resources=requested_resources_params_from_request_dto(request_dto.resources),
        description="Marimo workspace",
        to_be_deleted_at=request_dto.to_be_deleted_at,
        docker_image=request_dto.docker_image,
        marimo_password=request_dto.marimo_password,
    )

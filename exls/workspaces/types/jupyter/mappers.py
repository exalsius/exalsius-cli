from exls.workspaces.common.mappers import requested_resources_params_from_request_dto
from exls.workspaces.types.jupyter.dtos import DeployJupyterWorkspaceRequestDTO
from exls.workspaces.types.jupyter.gateway.dtos import DeployJupyterWorkspaceParams


def deploy_jupyter_workspace_params_from_request_dto(
    request_dto: DeployJupyterWorkspaceRequestDTO,
) -> DeployJupyterWorkspaceParams:
    return DeployJupyterWorkspaceParams(
        cluster_id=request_dto.cluster_id,
        name=request_dto.name,
        resources=requested_resources_params_from_request_dto(request_dto.resources),
        description="Jupyter workspace",
        to_be_deleted_at=request_dto.to_be_deleted_at,
        docker_image=request_dto.docker_image,
        jupyter_password=request_dto.jupyter_password,
    )

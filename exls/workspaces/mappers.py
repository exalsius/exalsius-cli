from exls.workspaces.dtos import DeployWorkspaceRequestDTO, WorkspaceResourcesRequestDTO
from exls.workspaces.gateway.dtos import DeployWorkspaceParams, RequestedResourcesParams


def requested_resources_params_from_request_dto(
    request_dto: WorkspaceResourcesRequestDTO,
) -> RequestedResourcesParams:
    return RequestedResourcesParams(
        gpu_count=request_dto.gpu_count,
        gpu_type=request_dto.gpu_type,
        gpu_vendor=request_dto.gpu_vendor,
        cpu_cores=request_dto.cpu_cores,
        memory_gb=request_dto.memory_gb,
        pvc_storage_gb=request_dto.pvc_storage_gb,
        ephemeral_storage_gb=request_dto.ephemeral_storage_gb,
    )


def deploy_workspace_request_dto_to_deploy_workspace_params(
    request_dto: DeployWorkspaceRequestDTO,
) -> DeployWorkspaceParams:
    resources: RequestedResourcesParams = RequestedResourcesParams(
        gpu_count=request_dto.resources.gpu_count,
        gpu_type=request_dto.resources.gpu_type,
        gpu_vendor=request_dto.resources.gpu_vendor,
        cpu_cores=request_dto.resources.cpu_cores,
        memory_gb=request_dto.resources.memory_gb,
        pvc_storage_gb=request_dto.resources.pvc_storage_gb,
        ephemeral_storage_gb=request_dto.resources.ephemeral_storage_gb,
    )
    return DeployWorkspaceParams(
        cluster_id=request_dto.cluster_id,
        template_name=request_dto.workspace_template_name,
        workspace_name=request_dto.workspace_name,
        resources=resources,
        description="",
        to_be_deleted_at=request_dto.to_be_deleted_at,
        variables=request_dto.variables,
    )

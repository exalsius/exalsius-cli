from exls.workspaces.common.dtos import WorkspaceResourcesRequestDTO
from exls.workspaces.common.gateway.dtos import RequestedResourcesParams


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

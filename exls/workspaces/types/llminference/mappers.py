from exls.workspaces.common.mappers import requested_resources_params_from_request_dto
from exls.workspaces.types.llminference.dtos import (
    DeployLLMInferenceWorkspaceRequestDTO,
)
from exls.workspaces.types.llminference.gateway.dtos import (
    DeployLLMInferenceWorkspaceParams,
)


def deploy_llm_inference_workspace_params_from_request_dto(
    request_dto: DeployLLMInferenceWorkspaceRequestDTO,
) -> DeployLLMInferenceWorkspaceParams:
    return DeployLLMInferenceWorkspaceParams(
        cluster_id=request_dto.cluster_id,
        name=request_dto.name,
        resources=requested_resources_params_from_request_dto(request_dto.resources),
        description="LLM Inference workspace",
        to_be_deleted_at=request_dto.to_be_deleted_at,
        docker_image=request_dto.docker_image,
        huggingface_model=request_dto.huggingface_model,
        huggingface_token=request_dto.huggingface_token,
        num_model_replicas=request_dto.num_model_replicas,
        tensor_parallel_size=request_dto.tensor_parallel_size,
        pipeline_parallel_size=request_dto.pipeline_parallel_size,
        pip_dependencies=request_dto.pip_dependencies,
        gpu_per_actor=request_dto.gpu_per_actor,
        cpu_per_actor=request_dto.cpu_per_actor,
        memory_gb_per_actor=request_dto.memory_gb_per_actor,
        ephemeral_storage_gb_per_actor=request_dto.ephemeral_storage_gb_per_actor,
    )

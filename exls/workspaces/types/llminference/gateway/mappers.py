from typing import Any, Dict

from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exls.workspaces.common.gateway.mappers import to_create_request
from exls.workspaces.types.llminference.gateway.dtos import (
    DeployLLMInferenceWorkspaceParams,
)


@to_create_request.register(DeployLLMInferenceWorkspaceParams)
def _(params: DeployLLMInferenceWorkspaceParams) -> WorkspaceCreateRequest:
    resources: Hardware = Hardware(
        gpu_count=params.resources.gpu_count,
        gpu_type=params.resources.gpu_type,
        gpu_vendor=params.resources.gpu_vendor,
        cpu_cores=params.resources.cpu_cores,
        memory_gb=params.resources.memory_gb,
        storage_gb=params.resources.pvc_storage_gb,
    )

    variables: Dict[str, Any] = {
        "deploymentName": params.name,
        "numModelReplicas": params.num_model_replicas,
        "tensorParallelSize": params.tensor_parallel_size,
        "pipelineParallelSize": params.pipeline_parallel_size,
        "cpuPerActor": params.cpu_per_actor,
        "gpuPerActor": params.gpu_per_actor,
        "runtimeEnvironmentPipPackages": params.pip_dependencies,
        "huggingfaceModel": params.huggingface_model,
    }
    if params.docker_image is not None:
        variables["deploymentImage"] = params.docker_image
    if params.huggingface_token is not None:
        variables["huggingfaceToken"] = params.huggingface_token
    if params.resources.ephemeral_storage_gb is not None:
        variables["ephemeralStorageGb"] = params.resources.ephemeral_storage_gb

    template: WorkspaceTemplate = WorkspaceTemplate(
        name=params.template_id,
        variables=variables,
    )

    return WorkspaceCreateRequest(
        cluster_id=params.cluster_id,
        name=params.name,
        description=params.description,
        resources=resources,
        template=template,
        to_be_deleted_at=params.to_be_deleted_at,
    )

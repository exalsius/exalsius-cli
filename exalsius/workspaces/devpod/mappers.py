from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exalsius.workspaces.devpod.domain import DeployDevPodWorkspaceParams
from exalsius.workspaces.gateway.mappers import to_create_request


@to_create_request.register(DeployDevPodWorkspaceParams)
def _(params: DeployDevPodWorkspaceParams) -> WorkspaceCreateRequest:
    resources: Hardware = Hardware(
        gpu_count=params.resources.gpu_count,
        gpu_type=params.resources.gpu_type,
        gpu_vendor=params.resources.gpu_vendor,
        cpu_cores=params.resources.cpu_cores,
        memory_gb=params.resources.memory_gb,
        storage_gb=params.resources.pvc_storage_gb,
    )

    template: WorkspaceTemplate = WorkspaceTemplate(
        name=params.template_id,
        variables={
            "deploymentName": params.name,
            "ephemeralStorageGb": params.resources.ephemeral_storage_gb,
            "deploymentImage": params.docker_image,
        },
    )

    return WorkspaceCreateRequest(
        cluster_id=params.cluster_id,
        name=params.name,
        description=params.description,
        resources=resources,
        template=template,
        to_be_deleted_at=params.to_be_deleted_at,
    )

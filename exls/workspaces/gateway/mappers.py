from typing import Any, Dict

from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exls.workspaces.gateway.dtos import DeployWorkspaceParams


def deploy_workspace_params_to_create_request(
    params: DeployWorkspaceParams,
) -> WorkspaceCreateRequest:
    """
    Convert WorkspaceDeployConfigDTO to SDK WorkspaceCreateRequest.

    Args:
        config: The workspace deployment configuration from file

    Returns:
        SDK WorkspaceCreateRequest ready for API call
    """

    variables: Dict[str, Any] = params.variables
    if params.resources.ephemeral_storage_gb is not None:
        variables["ephemeral_storage_gb"] = params.resources.ephemeral_storage_gb
    template = WorkspaceTemplate(
        name=params.template_name,
        description="",  # Template description is not stored in config
        variables=variables,
    )

    resources = Hardware(
        gpu_count=params.resources.gpu_count,
        gpu_vendor=params.resources.gpu_vendor,
        gpu_type=params.resources.gpu_type,
        cpu_cores=params.resources.cpu_cores,
        memory_gb=params.resources.memory_gb,
        storage_gb=params.resources.pvc_storage_gb,
    )

    return WorkspaceCreateRequest(
        name=params.workspace_name,
        cluster_id=params.cluster_id,
        template=template,
        resources=resources,
        description=params.description,
        to_be_deleted_at=params.to_be_deleted_at,
    )

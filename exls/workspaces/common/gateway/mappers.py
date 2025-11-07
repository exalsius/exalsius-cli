from functools import singledispatch

from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.common.gateway.dtos import DeployWorkspaceParams


@singledispatch
def to_create_request(params: DeployWorkspaceParams) -> WorkspaceCreateRequest:
    raise NotImplementedError(f"No mapper for type {type(params)}")


@to_create_request.register
def _(config: WorkspaceDeployConfigDTO) -> WorkspaceCreateRequest:
    """
    Convert WorkspaceDeployConfigDTO to SDK WorkspaceCreateRequest.

    Args:
        config: The workspace deployment configuration from file

    Returns:
        SDK WorkspaceCreateRequest ready for API call
    """
    template = WorkspaceTemplate(
        name=config.template_name,
        description="",  # Template description is not stored in config
        variables=config.variables,
    )

    resources = Hardware(
        gpu_count=config.resources.gpu_count,
        gpu_vendor=config.resources.gpu_vendor,
        gpu_type=config.resources.gpu_type,
        gpu_memory=config.resources.gpu_memory,
        cpu_cores=config.resources.cpu_cores,
        memory_gb=config.resources.memory_gb,
        storage_gb=config.resources.storage_gb,
    )

    return WorkspaceCreateRequest(
        name=config.workspace_name,
        cluster_id=config.cluster_id,
        template=template,
        resources=resources,
        description=None,  # Workspace description not in config
        to_be_deleted_at=None,  # Auto-deletion not yet supported
    )

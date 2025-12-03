from exalsius_api_client.models.node_hardware import NodeHardware as SdkNodeHardware
from exalsius_api_client.models.workspace import Workspace as SdkWorkspace
from exalsius_api_client.models.workspace_access_information import (
    WorkspaceAccessInformation as SdkWorkspaceAccessInformation,
)
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import (
    WorkspaceTemplate as SdkWorkspaceTemplate,
)

from exls.workspaces.core.domain import (
    Workspace,
    WorkspaceAccessInformation,
    WorkspaceAccessType,
    WorkspaceStatus,
)
from exls.workspaces.core.ports.gateway import DeployWorkspaceParameters


def workspace_access_information_from_sdk(
    sdk_model: SdkWorkspaceAccessInformation,
) -> WorkspaceAccessInformation:
    return WorkspaceAccessInformation(
        access_type=WorkspaceAccessType.from_str(sdk_model.access_type),
        access_protocol=sdk_model.access_protocol,
        external_ip=sdk_model.external_ip,
        port_number=sdk_model.port_number,
    )


def workspace_from_sdk(sdk_model: SdkWorkspace) -> Workspace:
    return Workspace(
        id=sdk_model.id or "",
        cluster_id=sdk_model.cluster_id or "",
        template_name=sdk_model.template.name,
        name=sdk_model.name,
        status=WorkspaceStatus.from_str(sdk_model.workspace_status or ""),
        created_at=sdk_model.created_at,
        access_information=[
            workspace_access_information_from_sdk(info)
            for info in (sdk_model.access_information or [])
        ],
    )


def deploy_workspace_parameters_to_create_request(
    parameters: DeployWorkspaceParameters,
) -> WorkspaceCreateRequest:
    """
    Convert DeployWorkspaceRequest to SDK WorkspaceCreateRequest.
    """

    template = SdkWorkspaceTemplate(
        name=parameters.template_name_id,
        description="",
        variables=parameters.variables,
    )

    resources = SdkNodeHardware(
        gpu_count=parameters.resources.gpu_count,
        gpu_vendor=parameters.resources.gpu_vendor,
        gpu_type=parameters.resources.gpu_type,
        cpu_cores=parameters.resources.cpu_cores,
        memory_gb=parameters.resources.memory_gb,
        storage_gb=parameters.resources.storage_gb,
    )

    return WorkspaceCreateRequest(
        name=parameters.workspace_name,
        cluster_id=parameters.cluster_id,
        template=template,
        resources=resources,
        description=parameters.description,
        to_be_deleted_at=parameters.to_be_deleted_at,
    )

from typing import Any, Dict

from exalsius_api_client.models.hardware import Hardware
from exalsius_api_client.models.workspace import Workspace as SdkWorkspace
from exalsius_api_client.models.workspace_access_information import (
    WorkspaceAccessInformation as SdkWorkspaceAccessInformation,
)
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import (
    WorkspaceTemplate as SdkWorkspaceTemplate,
)

from exls.workspaces.core.domain import (
    DeployWorkspaceRequest,
    Workspace,
    WorkspaceAccessInformation,
)


def workspace_access_information_from_sdk(
    sdk_model: SdkWorkspaceAccessInformation,
) -> WorkspaceAccessInformation:
    return WorkspaceAccessInformation(
        access_type=sdk_model.access_type,
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
        status=sdk_model.workspace_status or "",
        created_at=sdk_model.created_at,
        access_information=[
            workspace_access_information_from_sdk(info)
            for info in (sdk_model.access_information or [])
        ],
    )


def deploy_workspace_request_to_create_request(
    request: DeployWorkspaceRequest,
) -> WorkspaceCreateRequest:
    """
    Convert DeployWorkspaceRequest to SDK WorkspaceCreateRequest.
    """

    variables: Dict[str, Any] = request.variables
    template = SdkWorkspaceTemplate(
        name=request.template_name,
        description="",
        variables=variables,
    )

    resources = Hardware(
        gpu_count=request.resources.gpu_count,
        gpu_vendor=request.resources.gpu_vendor,
        gpu_type=request.resources.gpu_type,
        cpu_cores=request.resources.cpu_cores,
        memory_gb=request.resources.memory_gb,
        storage_gb=request.resources.pvc_storage_gb,
    )

    return WorkspaceCreateRequest(
        name=request.workspace_name,
        cluster_id=request.cluster_id,
        template=template,
        resources=resources,
        description=request.description,
        to_be_deleted_at=request.to_be_deleted_at,
    )

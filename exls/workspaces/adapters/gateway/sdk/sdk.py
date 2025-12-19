from typing import List, Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.node_hardware import NodeHardware
from exalsius_api_client.models.workspace import Workspace as SdkWorkspace
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exls.workspaces.adapters.gateway.gateway import WorkspacesGateway
from exls.workspaces.adapters.gateway.sdk.commands import (
    DeleteWorkspaceSdkCommand,
    DeployWorkspaceSdkCommand,
    GetWorkspaceSdkCommand,
    ListWorkspacesSdkCommand,
)
from exls.workspaces.core.domain import (
    Workspace,
    WorkspaceAccessInformation,
    WorkspaceAccessType,
    WorkspaceStatus,
)
from exls.workspaces.core.requests import DeployWorkspaceRequest


def _workspace_from_sdk(sdk_model: SdkWorkspace) -> Workspace:
    workspace_access_informations: List[WorkspaceAccessInformation] = [
        WorkspaceAccessInformation(
            access_type=WorkspaceAccessType.from_str(access_information.access_type),
            access_protocol=access_information.access_protocol,
            external_ips=access_information.external_ips or [],
            port_number=access_information.port_number,
        )
        for access_information in (sdk_model.access_information or [])
    ]

    return Workspace(
        id=sdk_model.id or "",
        cluster_id=sdk_model.cluster_id or "",
        template_name=sdk_model.template.name,
        name=sdk_model.name,
        status=WorkspaceStatus.from_str(sdk_model.workspace_status or ""),
        created_at=sdk_model.created_at,
        access_information=workspace_access_informations,
    )


def _deploy_workspace_request_to_sdk_create_request(
    parameters: DeployWorkspaceRequest,
) -> WorkspaceCreateRequest:
    """
    Convert DeployWorkspaceRequest to SDK WorkspaceCreateRequest.
    """

    template = WorkspaceTemplate(
        name=parameters.template_id,
        description="",
        variables=parameters.template_variables,
    )

    resources = NodeHardware(
        gpu_count=parameters.resources.gpu_count,
        gpu_type=parameters.resources.gpu_type,
        gpu_vendor=parameters.resources.gpu_vendor,
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


class SdkWorkspacesGateway(WorkspacesGateway):
    def __init__(self, workspaces_api: WorkspacesApi):
        self._workspaces_api = workspaces_api

    def list(self, cluster_id: Optional[str] = None) -> List[Workspace]:
        command: ListWorkspacesSdkCommand = ListWorkspacesSdkCommand(
            self._workspaces_api, cluster_id=cluster_id
        )
        response: WorkspacesListResponse = command.execute()
        return [
            _workspace_from_sdk(sdk_model=workspace)
            for workspace in response.workspaces
        ]

    def get(self, workspace_id: str) -> Workspace:
        command: GetWorkspaceSdkCommand = GetWorkspaceSdkCommand(
            self._workspaces_api, workspace_id=workspace_id
        )
        response: WorkspaceResponse = command.execute()
        return _workspace_from_sdk(sdk_model=response.workspace)

    def deploy(self, parameters: DeployWorkspaceRequest) -> str:
        """Deploy a workspace."""
        sdk_create_request: WorkspaceCreateRequest = (
            _deploy_workspace_request_to_sdk_create_request(parameters=parameters)
        )
        command: DeployWorkspaceSdkCommand = DeployWorkspaceSdkCommand(
            self._workspaces_api, request=sdk_create_request
        )
        response: WorkspaceCreateResponse = command.execute()
        return response.workspace_id

    def delete(self, workspace_id: str) -> str:
        command: DeleteWorkspaceSdkCommand = DeleteWorkspaceSdkCommand(
            self._workspaces_api, workspace_id=workspace_id
        )
        response: WorkspaceDeleteResponse = command.execute()
        return response.workspace_id

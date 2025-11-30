from typing import List

from pydantic import StrictStr

from exls.workspaces.adapters.dtos import WorkspaceAccessInformationDTO, WorkspaceDTO
from exls.workspaces.adapters.ui.dtos import DeployWorkspaceRequestDTO
from exls.workspaces.core.domain import Workspace
from exls.workspaces.core.requests import DeployWorkspaceRequest


def workspace_dto_from_domain(domain: Workspace) -> WorkspaceDTO:
    access_information: List[WorkspaceAccessInformationDTO] = []
    for info in domain.access_information:
        access_information.append(
            WorkspaceAccessInformationDTO(
                access_type=info.access_type,
                access_endpoint=info.endpoint,
            )
        )
    return WorkspaceDTO(
        id=domain.id,
        name=domain.name,
        cluster_id=domain.cluster_id,
        template_name=domain.template_name,
        status=domain.status.value,
        created_at=domain.created_at,
        access_information=access_information,
    )


def deploy_workspace_request_dto_from_domain(
    domain: DeployWorkspaceRequest, cluster_name: StrictStr
) -> DeployWorkspaceRequestDTO:
    return DeployWorkspaceRequestDTO(
        cluster_name=cluster_name,
        workspace_name=domain.workspace_name,
        workspace_template_name=domain.template_id,
        num_gpus=domain.resources.gpu_count,
        variables=str(domain.template_variables),
    )

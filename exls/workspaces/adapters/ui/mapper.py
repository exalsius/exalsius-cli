from typing import List

from pydantic import StrictStr

from exls.workspaces.adapters.dtos import (
    MultiNodeWorkspaceDTO,
    SingleNodeWorkspaceDTO,
    WorkspaceAccessInformationDTO,
    WorkspaceDTO,
)
from exls.workspaces.adapters.ui.dtos import (
    DeployMultiNodeWorkspaceRequestDTO,
    DeploySingleNodeWorkspaceRequestDTO,
)
from exls.workspaces.core.domain import Workspace
from exls.workspaces.core.requests import DeployWorkspaceRequest


def workspace_dto_from_domain(
    domain: Workspace, cluster_name: StrictStr
) -> WorkspaceDTO:
    access_information: List[WorkspaceAccessInformationDTO] = []
    for info in domain.access_information:
        access_information.append(
            WorkspaceAccessInformationDTO(
                type=info.access_type.value,
                protocol=info.access_protocol,
                ip=info.external_ips[0] if info.external_ips else None,
                port=info.port_number,
            )
        )
    return WorkspaceDTO(
        id=domain.id,
        name=domain.name,
        cluster_name=cluster_name,
        template_name=domain.template_name,
        status=domain.status.value,
        created_at=domain.created_at,
        access_information=access_information[0] if access_information else None,
    )


def single_node_workspace_dto_from_domain(
    domain: Workspace, cluster_name: StrictStr
) -> SingleNodeWorkspaceDTO:
    access_information: List[WorkspaceAccessInformationDTO] = []
    for info in domain.access_information:
        access_information.append(
            WorkspaceAccessInformationDTO(
                type=info.access_type.value,
                protocol=info.access_protocol,
                ip=info.external_ips[0] if info.external_ips else None,
                port=info.port_number,
            )
        )
    return SingleNodeWorkspaceDTO(
        id=domain.id,
        name=domain.name,
        cluster_name=cluster_name,
        template_name=domain.template_name,
        status=domain.status.value,
        created_at=domain.created_at,
        access_information=access_information[0] if access_information else None,
    )


def multi_node_workspace_dto_from_domain(
    domain: Workspace, total_nodes: int, gpu_types: str, cluster_name: StrictStr
) -> MultiNodeWorkspaceDTO:
    return MultiNodeWorkspaceDTO(
        id=domain.id,
        name=domain.name,
        cluster_name=cluster_name,
        template_name=domain.template_name,
        status=domain.status.value,
        created_at=domain.created_at,
        total_nodes=total_nodes,
        gpu_types=gpu_types,
        access_information=None,
    )


def deploy_single_node_workspace_request_dto_from_domain(
    domain: DeployWorkspaceRequest, cluster_name: StrictStr
) -> DeploySingleNodeWorkspaceRequestDTO:
    return DeploySingleNodeWorkspaceRequestDTO(
        cluster_name=cluster_name,
        workspace_name=domain.workspace_name,
        workspace_template_name=domain.template_id,
        num_gpus=domain.resources.gpu_count,
        variables=str(domain.template_variables),
    )


def deploy_multi_node_workspace_request_dto_from_domain(
    domain: DeployWorkspaceRequest,
    cluster_name: StrictStr,
    total_nodes: int,
    gpu_types: str,
) -> DeployMultiNodeWorkspaceRequestDTO:
    return DeployMultiNodeWorkspaceRequestDTO(
        cluster_name=cluster_name,
        workspace_name=domain.workspace_name,
        workspace_template_name=domain.template_id,
        total_nodes=total_nodes,
        gpu_types=gpu_types,
        variables=str(domain.template_variables),
    )

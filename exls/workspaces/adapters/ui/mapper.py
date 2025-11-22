from typing import List

from exls.workspaces.adapters.dtos import WorkspaceAccessInformationDTO, WorkspaceDTO
from exls.workspaces.core.domain import Workspace


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

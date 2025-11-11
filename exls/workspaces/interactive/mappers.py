from typing import List

import questionary

from exls.clusters.dtos import ClusterDTO
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.dtos import DeployWorkspaceRequestDTO, WorkspaceResourcesRequestDTO
from exls.workspaces.interactive.dtos import WorkspaceDeploymentConfigDTO


def cluster_to_questionary_choice(cluster: ClusterDTO) -> questionary.Choice:
    """Convert a ClusterDTO to a questionary Choice."""
    return questionary.Choice(
        title=f"{cluster.name} - {cluster.cluster_status}",
        value=cluster.id,
    )


def clusters_to_questionary_choices(
    clusters: List[ClusterDTO],
) -> List[questionary.Choice]:
    """Convert a list of ClusterDTOs to questionary Choices."""
    return [cluster_to_questionary_choice(cluster) for cluster in clusters]


def template_to_questionary_choice(
    template: WorkspaceTemplateDTO,
) -> questionary.Choice:
    """Convert a WorkspaceTemplateDTO to a questionary Choice."""
    return questionary.Choice(
        title=f"{template.name} - {template.description}",
        value=template.name,
    )


def templates_to_questionary_choices(
    templates: List[WorkspaceTemplateDTO],
) -> List[questionary.Choice]:
    """Convert a list of WorkspaceTemplateDTOs to questionary Choices."""
    return [template_to_questionary_choice(template) for template in templates]


def workspace_deployment_config_to_deploy_workspace_request_dto(
    deployment_config: WorkspaceDeploymentConfigDTO, cluster: ClusterDTO
) -> DeployWorkspaceRequestDTO:
    """Convert a WorkspaceDeploymentConfigDTO to a DeployWorkspaceRequestDTO."""
    resources: WorkspaceResourcesRequestDTO = WorkspaceResourcesRequestDTO(
        gpu_count=deployment_config.resources.gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=deployment_config.resources.cpu_cores,
        memory_gb=deployment_config.resources.memory_gb,
        pvc_storage_gb=deployment_config.resources.pvc_storage_gb,
    )

    return DeployWorkspaceRequestDTO(
        cluster_id=deployment_config.cluster_id,
        cluster_name=cluster.name,
        workspace_name=deployment_config.workspace_name,
        workspace_template_name=deployment_config.workspace_template_name,
        resources=resources,
        variables=deployment_config.variables,
        to_be_deleted_at=None,
    )
